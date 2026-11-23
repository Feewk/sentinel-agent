# Demo Video Script — Sentinel Agent (< 3 min)

Per build plan §f. One continuous, honest take. No sped-up footage of the
reactive hops — the ~seconds latency IS the pitch.
Rehearse signal (950, 7) beforehand; pre-run health-check.sh (all debt = 0).

| Time | Shot |
|---|---|
| 0:00–0:20 | Title card + one-sentence pitch. README architecture diagram on screen. Say the track rule back: "the AI is part of the running system." |
| 0:20–0:45 | The cast: SignalSource, AgentInbox, DecisionExecutor on Sepolia Etherscan; SentinelReactive on Lasna Reactscan — point at its Active subscriptions (Signal + DecisionRecorded). Show health-check output: debt = 0 everywhere. |
| 0:45–1:05 | Trigger in terminal: `cast send … emitSignal(950, 7)`. Open H1 on Etherscan, highlight the Signal log. |
| 1:05–1:30 | Lasna Reactscan: reactive tx H2 appears within seconds, links back to H1, CallbackRequest emitted. Follow to H3 on Etherscan: proxy → AgentInbox.recordCase, CaseOpened log, case # stored (950, 7, HIGH). |
| 1:30–2:10 | THE AI MOMENT: agent terminal shows the case arriving, the brief, the model's decision + rationale (ESCALATE). Show H4 submitDecision landing, DecisionRecorded firing. Nobody touched anything since the first cast send. |
| 2:10–2:40 | Hop 2: H5 on Lasna → H6 on Etherscan → ActionExecuted in DecisionExecutor; counters now ESCALATE = 1. |
| 2:40–2:58 | Recap slate: full H1–H6 hash table (same as README), repo URL, "built on Lasna + Sepolia testnets during the buildathon." End. |

Recording notes:
- Run the agent service with DECIDER=operator for the recording (supervised
  decision, logged) OR DECIDER=gemini where a Gemini key is available.
- Keep a backup take. Have explorer tabs pre-opened for every contract.
- If a hop is slow on camera, keep talking over the architecture diagram —
  do not cut the wait.
