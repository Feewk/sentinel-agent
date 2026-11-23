# Sentinel Agent — M1 Deployment & Proof (2026-11-23)

## Contracts
| Contract | Chain | Address |
|---|---|---|
| SignalSource | Ethereum Sepolia (11155111) | 0x3c62C3aa7881b8b571e6569B210849C404Ef6d8E |
| SentinelReactive | Reactive Lasna (5318007) | 0x3db0e1Eb83cffeeCCb1740a356c968c881335f1c |
| AgentInbox | Ethereum Sepolia (11155111) | 0x529A93Be2d526c686ecb0D5A6FB32fEea6382B3E |

Wallets: deployer 0xd225DC890959c52ae92D9264e98eb17dFe9bD46F · agent 0xC3470b8A1d90e81211BE71445edC215D97e042f5

## Funding trail
- User claimed 0.36 Sepolia ETH from their own browser (pk910 route blocked for the
  cloud browser by Cloudflare Turnstile; 5 faucets tried autonomously).
- lREACT exchange tx (Sepolia): 0x4b92398024a39a77aeb122845c58e33cec9bf06a01c4642f60c439c19b54e11a
  — 0.1 ETH → 10 lREACT to deployer on Lasna.

## M1 proof — first full reactive hop (emitSignal(950, 7))
| Step | Hash | Chain / block |
|---|---|---|
| H1 origin event | 0x83b3bf96bd2a739274918c64380660d31a1d8c7062b9021e22e820a9e0be0edc | Sepolia 12194422 |
| H2 reactive tx | 0x7731257e2e8eba5c5b5d7be74723c98fea82d636b381a32e35b31de0e5c39b21 | Lasna 9040708 |
| H3 callback | 0xb1275b03faf0213221d6b79d103e91825f951a3b00e8e17c4ae11df70283ffc0 | Sepolia 12194423 |

- AgentInbox case #1: value=950, tag=7, priority=1 (HIGH), exists=true
- Hop latency: case landed within ~15 seconds of H1
- debt(): SentinelReactive = 0 (Lasna system contract) · AgentInbox = 0 (Sepolia proxy)
- Reserves after run: RC 1.987 lREACT · Inbox ~0.05 ETH · deployer 0.21 Sepolia ETH / 7.90 lREACT

## M1 exit check: PASSED (2026-11-23 15:1x WIB)
Next: M2 — agent service (LLM decision loop) + submitDecision + DecisionExecutor (hop 2).
Note: M2 changes AgentInbox/SentinelReactive → full redeploy of the set expected.
