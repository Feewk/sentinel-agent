#!/usr/bin/env python3
"""Sentinel Agent — off-chain AI agent service.

The AI in the running system (Reactive Meets AI track rule): watches
AgentInbox.CaseOpened on Ethereum Sepolia, asks an LLM to triage each case
(action in {IGNORE, MONITOR, ESCALATE} + one-line rationale), and submits the
decision on-chain via AgentInbox.submitDecision — which triggers hop 2.

Decider backends (DECIDER env):
  operator — writes agent/requests/case-<id>.json and waits for a decision
             file agent/decisions/case-<id>.json written by a supervising
             LLM operator. Used for supervised/demo runs.
  gemini   — calls the Gemini API directly (needs GEMINI_API_KEY in env),
             model from GEMINI_MODEL (default gemini-2.5-flash), JSON-only
             response enforced by prompt + strict parsing.

Every brief, raw model output and tx hash is appended to agent/log.jsonl.
Idempotent by caseId (on-chain `decided` flag is the source of truth).
"""
import json
import os
import sys
import time
import urllib.request

sys.path.insert(0, os.path.expanduser("~/workspace/theta-hackathon/.venv/lib"))
from eth_account import Account
from eth_utils import keccak

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
ACTIONS = {0: "IGNORE", 1: "MONITOR", 2: "ESCALATE"}


def load_env(path):
    env = {}
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env[k] = v
    return env


ENV = load_env(os.path.join(ROOT, ".env"))
ADDRS = load_env(os.path.join(ROOT, "deployments", "m2-addresses.env"))
RPC = ENV["SEPOLIA_RPC_URL"]
INBOX = ADDRS["AGENT_INBOX"]
AGENT_KEY = ENV["AGENT_PRIVATE_KEY"]
DECIDER = os.environ.get("DECIDER", "operator")
POLL_SECONDS = int(os.environ.get("POLL_SECONDS", "8"))
OPERATOR_TIMEOUT = int(os.environ.get("OPERATOR_TIMEOUT", "900"))

acct = Account.from_key(AGENT_KEY)


def rpc(method, params):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    req = urllib.request.Request(RPC, data=body, headers={"content-type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        out = json.load(r)
    if "error" in out:
        raise RuntimeError(f"RPC {method}: {out['error']}")
    return out["result"]


def selector(sig):
    return keccak(text=sig)[:4]


def call_case(case_id):
    data = "0x" + (selector("cases(uint256)") + case_id.to_bytes(32, "big")).hex()
    raw = bytes.fromhex(rpc("eth_call", [{"to": INBOX, "data": data}, "latest"])[2:])
    words = [int.from_bytes(raw[i:i + 32], "big") for i in range(0, 7 * 32, 32)]
    return {"value": words[0], "tag": words[1], "priority": words[2],
            "exists": bool(words[3]), "decided": bool(words[4]), "action": words[5]}


def case_count():
    data = "0x" + selector("caseCount()").hex()
    return int(rpc("eth_call", [{"to": INBOX, "data": data}, "latest"]), 16)


def brief_for(case_id, case, history):
    return {
        "caseId": case_id,
        "value": case["value"],
        "tag": case["tag"],
        "priority": "HIGH" if case["priority"] == 1 else "NORMAL",
        "recentCases": history[-5:],
        "instruction": (
            "You are the triage model inside Sentinel Agent. A signal just landed "
            "on-chain. value is the signal magnitude (0-1000 scale, >=500 was "
            "flagged HIGH priority by the on-chain triage), tag is the signal "
            "class (7 = critical-infrastructure pattern, 3 = routine telemetry, "
            "other = misc). Decide exactly one action: IGNORE (noise, no "
            "follow-up), MONITOR (watch, no intervention), or ESCALATE "
            "(act now). Respond with JSON only: "
            '{"action": "IGNORE"|"MONITOR"|"ESCALATE", "rationale": "<one line>"}'
        ),
    }


def decide_gemini(brief):
    import urllib.request as u
    key = os.environ["GEMINI_API_KEY"]
    model = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
    payload = {"contents": [{"parts": [{"text": json.dumps(brief)}]}],
               "generationConfig": {"responseMimeType": "application/json"}}
    req = u.Request(
        f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
        data=json.dumps(payload).encode(),
        headers={"content-type": "application/json", "x-goog-api-key": key})
    with u.urlopen(req, timeout=60) as r:
        out = json.load(r)
    text = out["candidates"][0]["content"]["parts"][0]["text"]
    return text


def decide_operator(brief):
    req_dir = os.path.join(HERE, "requests")
    dec_dir = os.path.join(HERE, "decisions")
    os.makedirs(req_dir, exist_ok=True)
    os.makedirs(dec_dir, exist_ok=True)
    cid = brief["caseId"]
    with open(os.path.join(req_dir, f"case-{cid}.json"), "w") as f:
        json.dump(brief, f, indent=2)
    print(f"[agent] case {cid}: decision request written, waiting for operator...", flush=True)
    deadline = time.time() + OPERATOR_TIMEOUT
    path = os.path.join(dec_dir, f"case-{cid}.json")
    while time.time() < deadline:
        if os.path.exists(path):
            with open(path) as f:
                return f.read()
        time.sleep(3)
    raise TimeoutError(f"operator decision for case {cid} timed out — case left undecided, nothing guessed")


def parse_decision(raw):
    obj = json.loads(raw)
    name = str(obj["action"]).upper()
    rev = {v: k for k, v in ACTIONS.items()}
    if name not in rev:
        raise ValueError(f"bad action in model output: {raw!r}")
    rationale = str(obj["rationale"]).strip()
    if not rationale:
        raise ValueError("empty rationale")
    return rev[name], rationale


def submit_decision(case_id, action, rationale):
    rationale_hash = keccak(text=rationale)
    data = (selector("submitDecision(uint256,uint8,bytes32)")
            + case_id.to_bytes(32, "big")
            + action.to_bytes(32, "big")
            + rationale_hash)
    nonce = int(rpc("eth_getTransactionCount", [acct.address, "pending"]), 16)
    gas_price = int(rpc("eth_gasPrice", []), 16)
    tx = {"to": INBOX, "value": 0, "gas": 200_000, "gasPrice": gas_price * 2,
          "nonce": nonce, "chainId": 11155111, "data": data}
    signed = acct.sign_transaction(tx)
    tx_hash = rpc("eth_sendRawTransaction", ["0x" + signed.raw_transaction.hex()])
    return tx_hash


def log(entry):
    entry["ts"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    with open(os.path.join(HERE, "log.jsonl"), "a") as f:
        f.write(json.dumps(entry) + "\n")
    print(f"[agent] {json.dumps(entry)}", flush=True)


def main():
    history = []
    print(f"[agent] watching {INBOX} as {acct.address} (decider={DECIDER})", flush=True)
    while True:
        try:
            n = case_count()
            for cid in range(1, n + 1):
                case = call_case(cid)
                if not case["exists"] or case["decided"]:
                    continue
                if any(h["caseId"] == cid and h.get("submitted") for h in history):
                    continue
                brief = brief_for(cid, case, history)
                raw = decide_gemini(brief) if DECIDER == "gemini" else decide_operator(brief)
                action, rationale = parse_decision(raw)
                tx_hash = submit_decision(cid, action, rationale)
                rec = {"caseId": cid, "brief": brief, "rawModelOutput": raw,
                       "action": ACTIONS[action], "rationale": rationale,
                       "submitDecisionTx": tx_hash, "submitted": True}
                history.append(rec)
                log(rec)
        except Exception as e:  # keep watching; undecided cases retry next poll
            print(f"[agent] error: {e}", flush=True)
        time.sleep(POLL_SECONDS)


if __name__ == "__main__":
    main()
