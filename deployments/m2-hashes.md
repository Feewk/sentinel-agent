# Sentinel Agent — M2 Deployment & Proof (2026-11-23)

## Contracts (M2 set; SignalSource reused from M1)
| Contract | Chain | Address |
|---|---|---|
| SignalSource | Ethereum Sepolia | 0x3c62C3aa7881b8b571e6569B210849C404Ef6d8E |
| SentinelReactive v2 | Reactive Lasna | 0x529A93Be2d526c686ecb0D5A6FB32fEea6382B3E |
| AgentInbox v2 | Ethereum Sepolia | 0x7b9155f7B50559ea2Bb730C0939B59A522bF069E |
| DecisionExecutor | Ethereum Sepolia | 0x6e7f241817707dE3B85E470606e2028EC88eF2E4 |

Agent EOA: 0xC3470b8A1d90e81211BE71445edC215D97e042f5 (funded 0.02 ETH)
Agent service: agent/agent.py — operator decider backend for these runs
(supervising LLM = Muse, decisions logged in agent/log.jsonl);
gemini backend included in code. NOTE: the Gemini connector credential is
not available inside this side-chat sandbox (403 from credential service),
so the live Gemini backend could not be exercised from here.

## Scenario A — critical signal (950, tag 7) → ESCALATE
| Step | Hash |
|---|---|
| H1 origin Signal | 0xe90ef7b9f6f38cc368700825979a708f6a7fe9bebd1e818f811b9d87ef443384 |
| H2 reactive (Lasna 9041388) | 0xf78fd06c847cfbd9c09fb8c0dbd8aff6d510ef4c4e20a1072e8827539ad9591a |
| H3 callback CaseOpened (Sepolia 12194478) | 0x50e8c7ff98ac28280ec7a227eaf50905742337083c490331b23ebdef25e57e46 |
| H4 agent submitDecision (Sepolia 12194480) | 0x10c25f1bb23cbe5f654a85a282df822e3030d05328fce52ac6b95fb7e1c93de5 |
| H5 reactive hop-2 (Lasna 9041423) | 0x662ce245f050d50074c9919ccff0ca6ec2a39df90c4602d8e248a67c81dc7948 |
| H6 callback ActionExecuted (Sepolia 12194481) | 0x5105370feb1c62e30f92db51862d79458f13ba2ebec4ad030308a0cd8e9a6bd1 |

Rationale: "Value 950 with tag 7 matches the critical-infrastructure pattern
and was flagged HIGH priority on-chain; escalate for immediate action."

## Scenario B — routine signal (120, tag 3) → MONITOR
| Step | Hash |
|---|---|
| H1 origin Signal | 0xc30cb4d0cc6e33b2f2dec89fefc79f54c5a1b51043fee088c7222c9d23f33cea |
| H2 reactive (Lasna 9041447) | 0xdf88344924db9684caa1baf904db1eac73c874decc34c1f673dc62e7f0c33a67 |
| H3 callback CaseOpened (Sepolia 12194483) | 0x1d476678c7992ddaa23f03eba901984ab1bbc7434265ec88ff485c5c780d53e5 |
| H4 agent submitDecision (Sepolia 12194485) | 0x36789ff0f868269d1e4ad57f3755e730c11e1d34fb49c8e935493399e9fd7179 |
| H5 reactive hop-2 (Lasna 9041492) | 0x0ad51db0138af530692b9134f57ff1ce7998d467f044c2bab2a2994afd4bdbd5 |
| H6 callback ActionExecuted (Sepolia 12194486) | 0x7e5bfbbfee3d5f1b692075242ba425906ae555e77c99791e5d7d2b067cd65e8e |

Rationale: "Value 120 with tag 3 is routine telemetry at NORMAL priority;
no intervention warranted, keep the stream under watch."
On-chain rationaleHash verified = keccak256(rationale) 0x5301a16e…a4cb9b.

## M2 exit check: PASSED (2026-11-23 15:2x WIB)
- DecisionExecutor: totalExecuted=2, counts IGNORE=0 / MONITOR=1 / ESCALATE=1
- debt() = 0 on all three contracts after both runs
- Balances after M2: deployer 0.090 Sepolia ETH / 5.75 lREACT · RC 1.95 lREACT · agent ~0.02 ETH
- Known wrinkle: public Sepolia RPC dropped some polls mid-run (service
  retries by design); one log.jsonl entry was backfilled from chain data.
