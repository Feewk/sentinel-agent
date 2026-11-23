# Sentinel Agent — Status (Workspace Theta, updated 2026-11-23 15:4x WIB)

- M0 DONE: RPC pinned (Lasna lasna-rpc.rnk.dev = 5318007), Foundry 1.10,
  wallets derived, funding in (user faucet claim 0.36 ETH → 10 lREACT).
- M1 DONE: single hop live, H1–H3 captured (deployments/m1-hashes.md).
- M2 DONE: two-hop loop + AI agent, 6 hashes × 2 scenarios
  (deployments/m2-hashes.md), executor totalExecuted=2, debt=0.
- M3 DONE except Sourcify verification (retry blocked on user approval
  after a timed-out approval card; reported to user 15:36 WIB).
  Negative tests 5/5, health-check clean, README complete.
- M4 IN PROGRESS:
  - Public repo LIVE: https://github.com/Feewk/sentinel-agent
  - Beta validation REQUESTED to Workspace Core 2026-11-23 (verdict must be
    pushed to Theta chat per Protokol Dorong Vonis) — awaiting verdict.
  - Demo video: script ready (DEMO-SCRIPT.md), not yet recorded.
  - BUIDL submit: after Beta verdict + video. Deadline 5 Dec 2026 20:00 UTC.
- Decider note: M2 runs used operator backend (supervising LLM) — Gemini
  connector credential is refused inside this side-chat sandbox (403);
  gemini backend exists in agent/agent.py, untested live from here.
