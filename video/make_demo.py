#!/usr/bin/env python3
"""Build the Sentinel Agent demo video from REAL run evidence.

Renders terminal-style slides (real commands, real tx hashes, real outputs
from the 2026-11-23 live testnet runs) and assembles them with ffmpeg.
This is a walkthrough of verifiable on-chain proof — every hash below can be
checked on sepolia.etherscan.io / lasna.reactscan.net.
Output: video/sentinel-demo.mp4 (< 3 minutes, silent, captioned slides).
"""
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 1280, 720
BG = (13, 17, 23)
FG = (201, 209, 217)
GREEN = (63, 185, 80)
BLUE = (88, 166, 255)
YELLOW = (210, 153, 34)
DIM = (139, 148, 158)

MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
MONO_B = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"


def font(size, bold=False):
    return ImageFont.truetype(MONO_B if bold else MONO, size)


# (duration_seconds, title, [(text, color, bold, size), ...])
SLIDES = [
    (10, None, [
        ("SENTINEL AGENT", GREEN, True, 54),
        ("", FG, False, 24),
        ("Autonomous signal triage on Reactive Network", FG, False, 28),
        ("Reactive Omni Buildathon — Reactive Meets AI", BLUE, False, 24),
        ("", FG, False, 24),
        ("Ethereum Sepolia  x  Reactive Lasna (testnets)", DIM, False, 22),
    ]),
    (16, "WHY THIS TRACK", [
        ("Track rule: \"the AI has to be part of the running", FG, False, 24),
        ("system, not just the tool you used to write the code.\"", FG, False, 24),
        ("", FG, False, 24),
        ("In Sentinel Agent, a live LLM sits INSIDE the loop:", YELLOW, False, 24),
        ("it reads each case the reactive contract files,", FG, False, 24),
        ("decides IGNORE / MONITOR / ESCALATE, and its decision", FG, False, 24),
        ("is executed on-chain by a second reactive hop.", FG, False, 24),
        ("No keeper. No cron. No human in the loop.", GREEN, False, 24),
    ]),
    (18, "ARCHITECTURE — THE TWO-HOP LOOP", [
        ("SignalSource (Sepolia)   emitSignal(value, tag)      H1", FG, False, 23),
        ("        |  Signal event", DIM, False, 23),
        ("SentinelReactive (Lasna) react() — priority triage   H2", FG, False, 23),
        ("        |  callback recordCase()", DIM, False, 23),
        ("AgentInbox (Sepolia)     CaseOpened                  H3", FG, False, 23),
        ("        |  event watched by", DIM, False, 23),
        ("AI AGENT (off-chain)     LLM decides + rationale", YELLOW, False, 23),
        ("        |  submitDecision(caseId, action, hash)     H4", DIM, False, 23),
        ("SentinelReactive (Lasna) react() on DecisionRecorded H5", FG, False, 23),
        ("        |  callback execute()", DIM, False, 23),
        ("DecisionExecutor         ActionExecuted + counters   H6", FG, False, 23),
    ]),
    (16, "THE CAST — DEPLOYED & VERIFIABLE", [
        ("SignalSource      Sepolia  0x3c62C3aa...404Ef6d8E", FG, False, 23),
        ("SentinelReactive  Lasna    0x529A93Be...Eea6382B3E", FG, False, 23),
        ("AgentInbox        Sepolia  0x7b9155f7...22bF069E", FG, False, 23),
        ("DecisionExecutor  Sepolia  0x6e7f2418...EC88eF2E4", FG, False, 23),
        ("", FG, False, 23),
        ("Reactscan shows SentinelReactive subscriptions ACTIVE:", FG, False, 23),
        ("  Signal(address,uint256,uint256)      on Sepolia", BLUE, False, 23),
        ("  DecisionRecorded(uint256,uint8)      on Sepolia", BLUE, False, 23),
        ("", FG, False, 23),
        ("$ bash script/health-check.sh", GREEN, False, 23),
        ("  SentinelReactive  debt 0   AgentInbox  debt 0", FG, False, 23),
        ("  DecisionExecutor  debt 0   reserves funded", FG, False, 23),
    ]),
    (14, "FIRE A CRITICAL SIGNAL", [
        ("$ cast send $SIGNAL_SOURCE \\", GREEN, False, 24),
        ("    \"emitSignal(uint256,uint256)\" 950 7", GREEN, False, 24),
        ("", FG, False, 24),
        ("status            1 (success)", FG, False, 24),
        ("H1  0xe90ef7b9f6f38cc368700825979a708f6a7fe9bebd1", BLUE, False, 22),
        ("    e818f811b9d87ef443384          (Sepolia)", BLUE, False, 22),
        ("", FG, False, 24),
        ("Signal log: sender=deployer  value=950  tag=7", FG, False, 24),
        ("tag 7 = critical-infrastructure pattern", DIM, False, 24),
    ]),
    (16, "HOP 1 LANDS — CASE FILED IN ~15 SECONDS", [
        ("Lasna — SentinelReactive.react() fired:", FG, False, 24),
        ("H2  0xf78fd06c847cfbd9c09fb8c0dbd8aff6d510ef4c4", BLUE, False, 22),
        ("    e20a1072e8827539ad9591a          (Lasna)", BLUE, False, 22),
        ("    deterministic triage: 950 >= 500 -> priority HIGH", FG, False, 24),
        ("    (priority only — the DECISION is not made here)", DIM, False, 24),
        ("", FG, False, 24),
        ("Sepolia — callback proxy calls AgentInbox.recordCase:", FG, False, 24),
        ("H3  0x50e8c7ff98ac28280ec7a227eaf50905742337083c", BLUE, False, 22),
        ("    490331b23ebdef25e57e46          (Sepolia)", BLUE, False, 22),
        ("    CaseOpened(1, 950, 7, HIGH) — case #1 stored", FG, False, 24),
    ]),
    (20, "THE AI MOMENT — THE MODEL DECIDES", [
        ("[agent] CaseOpened case 1: value=950 tag=7 priority=HIGH", FG, False, 22),
        ("[agent] brief -> LLM (actions: IGNORE|MONITOR|ESCALATE)", FG, False, 22),
        ("", FG, False, 22),
        ("[model] {\"action\": \"ESCALATE\",", YELLOW, False, 22),
        ("         \"rationale\": \"Value 950 with tag 7 matches", YELLOW, False, 22),
        ("         the critical-infrastructure pattern and was", YELLOW, False, 22),
        ("         flagged HIGH priority on-chain; escalate", YELLOW, False, 22),
        ("         for immediate action.\"}", YELLOW, False, 22),
        ("", FG, False, 22),
        ("[agent] submitDecision(1, ESCALATE, keccak(rationale))", FG, False, 22),
        ("H4  0x10c25f1bb23cbe5f654a85a282df822e3030d05328f", BLUE, False, 22),
        ("    ce52ac6b95fb7e1c93de5           (Sepolia)", BLUE, False, 22),
        ("Nobody touched anything after the first cast send.", GREEN, False, 22),
    ]),
    (16, "HOP 2 — THE DECISION EXECUTES ON-CHAIN", [
        ("Lasna — react() fires on DecisionRecorded:", FG, False, 24),
        ("H5  0x662ce245f050d50074c9919ccff0ca6ec2a39df90c", BLUE, False, 22),
        ("    4602d8e248a67c81dc7948          (Lasna)", BLUE, False, 22),
        ("", FG, False, 24),
        ("Sepolia — callback proxy calls DecisionExecutor.execute:", FG, False, 24),
        ("H6  0x5105370feb1c62e30f92db51862d79458f13ba2ebe", BLUE, False, 22),
        ("    c4ad030308a0cd8e9a6bd1          (Sepolia)", BLUE, False, 22),
        ("    ActionExecuted(1, ESCALATE)", FG, False, 24),
        ("", FG, False, 24),
        ("A second run (120, tag 3 = routine telemetry)", FG, False, 24),
        ("was decided MONITOR and executed the same way.", FG, False, 24),
        ("Executor totals: executed=2  ESCALATE=1  MONITOR=1", GREEN, False, 24),
    ]),
    (18, "PROOF — EVERY HASH VERIFIABLE", [
        ("Scenario A (950/7 -> ESCALATE)      Scenario B (120/3 -> MONITOR)", FG, True, 19),
        ("H1 e90ef7b9...ef443384              H1 c30cb4d0...d23f33cea", FG, False, 19),
        ("H2 f78fd06c...ad9591a               H2 df883449...33a67", FG, False, 19),
        ("H3 50e8c7ff...25e57e46              H3 1d476678...c780d53e5", FG, False, 19),
        ("H4 10c25f1b...7e1c93de5             H4 36789ff0...99399e9fd7179", FG, False, 19),
        ("H5 662ce245...81dc7948              H5 0ad51db0...4bdbd5", FG, False, 19),
        ("H6 5105370f...d8e9a6bd1             H6 7e5bfbbf...2b067cd65e8e", FG, False, 19),
        ("", FG, False, 19),
        ("Full hashes + explorer links: README in the repo.", BLUE, False, 19),
        ("Case 2 rationaleHash verified on-chain =", FG, False, 19),
        ("keccak256(model rationale) — the model's words,", FG, False, 19),
        ("provably the ones that were submitted.", FG, False, 19),
    ]),
    (10, None, [
        ("SENTINEL AGENT", GREEN, True, 40),
        ("", FG, False, 24),
        ("github.com/Feewk/sentinel-agent", BLUE, False, 26),
        ("", FG, False, 24),
        ("Built on Lasna + Sepolia testnets", FG, False, 24),
        ("during the Reactive Omni Buildathon.", FG, False, 24),
    ]),
]


def render(idx, title, lines):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    y = 56
    if title:
        d.text((56, y), title, font=font(26, True), fill=GREEN)
        y += 52
        d.line([(56, y), (W - 56, y)], fill=DIM, width=1)
        y += 30
    for text, color, bold, size in lines:
        d.text((56, y), text, font=font(size, bold), fill=color)
        y += int(size * 1.45)
    path = os.path.join(HERE, f"slide-{idx:02d}.png")
    img.save(path)
    return path


def main():
    total = sum(s[0] for s in SLIDES)
    print(f"{len(SLIDES)} slides, total {total}s")
    assert total < 180, "must stay under 3 minutes"
    concat = os.path.join(HERE, "concat.txt")
    with open(concat, "w") as f:
        for i, (dur, title, lines) in enumerate(SLIDES):
            p = render(i, title, lines)
            f.write(f"file '{p}'\nduration {dur}\n")
        f.write(f"file '{os.path.join(HERE, f'slide-{len(SLIDES)-1:02d}.png')}'\n")
    out = os.path.join(HERE, "sentinel-demo.mp4")
    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat,
        "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", "30",
        "-c:a", "aac", "-shortest", out,
    ], check=True, capture_output=True)
    size = os.path.getsize(out)
    print(f"wrote {out} ({size/1e6:.2f} MB)")


if __name__ == "__main__":
    main()
