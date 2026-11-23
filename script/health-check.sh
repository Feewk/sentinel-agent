#!/usr/bin/env bash
# Sentinel Agent — pre-demo health drill (plan M3).
# Prints debt() + reserves for every contract on both chains.
# Rule: never start a demo run with debt > 0 anywhere.
set -euo pipefail
cd "$(dirname "$0")/.."
set -a; source .env; source deployments/m2-addresses.env; set +a
export PATH="$HOME/.foundry/bin:$PATH"

SYSTEM=0x8888888888888888888888888888888888888888
PROXY=0xAa14d9Cd0f788Ca23d11805986C1d8bd035D23b4
fmt() { python3 -c "import sys; print(f'{int(sys.argv[1])/1e18:.4f}')" "$1"; }

echo "== Lasna (lREACT)"
echo "SentinelReactive  balance $(fmt "$(cast balance "$SENTINEL_REACTIVE" --rpc-url "$LASNA_RPC_URL")")  debt $(cast call $SYSTEM "debt(address)(uint256)" "$SENTINEL_REACTIVE" --rpc-url "$LASNA_RPC_URL")"
echo "Deployer          balance $(fmt "$(cast balance "$DEPLOYER_ADDRESS" --rpc-url "$LASNA_RPC_URL")")"
echo "== Sepolia (ETH)"
echo "AgentInbox        balance $(fmt "$(cast balance "$AGENT_INBOX" --rpc-url "$SEPOLIA_RPC_URL")")  debt $(cast call $PROXY "debt(address)(uint256)" "$AGENT_INBOX" --rpc-url "$SEPOLIA_RPC_URL")"
echo "DecisionExecutor  balance $(fmt "$(cast balance "$DECISION_EXECUTOR" --rpc-url "$SEPOLIA_RPC_URL")")  debt $(cast call $PROXY "debt(address)(uint256)" "$DECISION_EXECUTOR" --rpc-url "$SEPOLIA_RPC_URL")"
echo "Deployer          balance $(fmt "$(cast balance "$DEPLOYER_ADDRESS" --rpc-url "$SEPOLIA_RPC_URL")")"
echo "Agent EOA         balance $(fmt "$(cast balance "$AGENT_ADDRESS" --rpc-url "$SEPOLIA_RPC_URL")")"
echo "== Loop state"
echo "Cases opened:     $(cast call "$AGENT_INBOX" "caseCount()(uint256)" --rpc-url "$SEPOLIA_RPC_URL")"
echo "Actions executed: $(cast call "$DECISION_EXECUTOR" "totalExecuted()(uint256)" --rpc-url "$SEPOLIA_RPC_URL") (IGNORE $(cast call "$DECISION_EXECUTOR" "actionCounts(uint256)(uint256)" 0 --rpc-url "$SEPOLIA_RPC_URL") / MONITOR $(cast call "$DECISION_EXECUTOR" "actionCounts(uint256)(uint256)" 1 --rpc-url "$SEPOLIA_RPC_URL") / ESCALATE $(cast call "$DECISION_EXECUTOR" "actionCounts(uint256)(uint256)" 2 --rpc-url "$SEPOLIA_RPC_URL"))"
