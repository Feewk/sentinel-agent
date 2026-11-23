#!/usr/bin/env bash
# Sentinel Agent — M2 deployment (full set redeploy; SignalSource reused from M1).
# Order: RC (Lasna) → AgentInbox v2 (Sepolia) → DecisionExecutor (Sepolia)
#        → setAgentInbox (also subscribes hop-2) → setDecisionExecutor
#        → fund agent EOA with 0.02 Sepolia ETH for submitDecision gas.
set -euo pipefail
cd "$(dirname "$0")/.."
set -a; source .env; source deployments/m1-addresses.env; set +a
export PATH="$HOME/.foundry/bin:$PATH"

SEPOLIA_PROXY=0xAa14d9Cd0f788Ca23d11805986C1d8bd035D23b4
LOG=deployments/m2.log
mkdir -p deployments
parse() { python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('deployedTo') or d.get('contractAddress') or d['receipt']['contractAddress'])"; }

echo "SignalSource (reused): $SIGNAL_SOURCE"
echo "== 1. SentinelReactive v2 (Lasna, 2 lREACT reserve)"
RC=$(forge create --broadcast src/SentinelReactive.sol:SentinelReactive --rpc-url "$LASNA_RPC_URL" \
  --private-key "$DEPLOYER_PRIVATE_KEY" --value 2ether --json \
  --constructor-args "$SIGNAL_SOURCE" | parse)
echo "SentinelReactive: $RC" | tee -a "$LOG"

echo "== 2. AgentInbox v2 (Sepolia, 0.05 ETH reserve)"
INBOX=$(forge create --broadcast src/AgentInbox.sol:AgentInbox --rpc-url "$SEPOLIA_RPC_URL" \
  --private-key "$DEPLOYER_PRIVATE_KEY" --value 0.05ether --json \
  --constructor-args "$SEPOLIA_PROXY" "$RC" "$AGENT_ADDRESS" | parse)
echo "AgentInbox: $INBOX" | tee -a "$LOG"

echo "== 3. DecisionExecutor (Sepolia, 0.05 ETH reserve)"
EXEC=$(forge create --broadcast src/DecisionExecutor.sol:DecisionExecutor --rpc-url "$SEPOLIA_RPC_URL" \
  --private-key "$DEPLOYER_PRIVATE_KEY" --value 0.05ether --json \
  --constructor-args "$SEPOLIA_PROXY" "$RC" | parse)
echo "DecisionExecutor: $EXEC" | tee -a "$LOG"

echo "== 4. setAgentInbox + setDecisionExecutor (Lasna)"
cast send "$RC" "setAgentInbox(address)" "$INBOX" --rpc-url "$LASNA_RPC_URL" \
  --private-key "$DEPLOYER_PRIVATE_KEY" > /dev/null
cast send "$RC" "setDecisionExecutor(address)" "$EXEC" --rpc-url "$LASNA_RPC_URL" \
  --private-key "$DEPLOYER_PRIVATE_KEY" > /dev/null
echo "wired" | tee -a "$LOG"

echo "== 5. Fund agent EOA (0.02 ETH)"
cast send "$AGENT_ADDRESS" --value 0.02ether --rpc-url "$SEPOLIA_RPC_URL" \
  --private-key "$DEPLOYER_PRIVATE_KEY" > /dev/null
echo "agent funded: $(cast balance "$AGENT_ADDRESS" --rpc-url "$SEPOLIA_RPC_URL")" | tee -a "$LOG"

cat > deployments/m2-addresses.env <<EOF
SIGNAL_SOURCE=$SIGNAL_SOURCE
SENTINEL_REACTIVE=$RC
AGENT_INBOX=$INBOX
DECISION_EXECUTOR=$EXEC
EOF
echo "Done. Addresses in deployments/m2-addresses.env"
