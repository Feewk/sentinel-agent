#!/usr/bin/env bash
# Sentinel Agent — M1 deployment (forced order, plan §a):
#   1. SignalSource        (Sepolia)
#   2. SentinelReactive    (Lasna, funded with lREACT at deploy)
#   3. AgentInbox          (Sepolia, proxy + RC address immutable)
#   4. setAgentInbox       (Lasna, owner-only setter)
#   5. Fund AgentInbox via proxy deposit path (payable receive / coverDebt)
# Aborts if deployer balances are zero on either chain.
set -euo pipefail
cd "$(dirname "$0")/.."
set -a; source .env; set +a
export PATH="$HOME/.foundry/bin:$PATH"

SEPOLIA_PROXY=0xAa14d9Cd0f788Ca23d11805986C1d8bd035D23b4
LOG=deployments/m1.log
mkdir -p deployments

bal() { cast balance "$DEPLOYER_ADDRESS" --rpc-url "$1"; }
echo "Sepolia balance: $(bal "$SEPOLIA_RPC_URL")"
echo "Lasna balance:   $(bal "$LASNA_RPC_URL")"
[ "$(bal "$SEPOLIA_RPC_URL")" != "0" ] || { echo "ABORT: deployer has 0 Sepolia ETH — fund via faucet first"; exit 1; }
[ "$(bal "$LASNA_RPC_URL")" != "0" ] || { echo "ABORT: deployer has 0 lREACT — run the lREACT faucet exchange first"; exit 1; }

echo "== 1. SignalSource (Sepolia)" | tee -a "$LOG"
if [ -f deployments/m1-signal.txt ]; then
  SIGNAL=$(cat deployments/m1-signal.txt)
else
  SIGNAL=$(forge create --broadcast src/SignalSource.sol:SignalSource --rpc-url "$SEPOLIA_RPC_URL" \
    --private-key "$DEPLOYER_PRIVATE_KEY" --json | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('deployedTo') or d.get('contractAddress') or d['receipt']['contractAddress'])")
  echo -n "$SIGNAL" > deployments/m1-signal.txt
fi
echo "SignalSource: $SIGNAL" | tee -a "$LOG"

echo "== 2. SentinelReactive (Lasna, 2 lREACT reserve)" | tee -a "$LOG"
RC=$(forge create --broadcast src/SentinelReactive.sol:SentinelReactive --rpc-url "$LASNA_RPC_URL" \
  --private-key "$DEPLOYER_PRIVATE_KEY" --value 2ether --json \
  --constructor-args "$SIGNAL" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('deployedTo') or d.get('contractAddress') or d['receipt']['contractAddress'])")
echo "SentinelReactive: $RC" | tee -a "$LOG"

echo "== 3. AgentInbox (Sepolia, 0.05 ETH reserve)" | tee -a "$LOG"
INBOX=$(forge create --broadcast src/AgentInbox.sol:AgentInbox --rpc-url "$SEPOLIA_RPC_URL" \
  --private-key "$DEPLOYER_PRIVATE_KEY" --value 0.05ether --json \
  --constructor-args "$SEPOLIA_PROXY" "$RC" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('deployedTo') or d.get('contractAddress') or d['receipt']['contractAddress'])")
echo "AgentInbox: $INBOX" | tee -a "$LOG"

echo "== 4. setAgentInbox on SentinelReactive" | tee -a "$LOG"
cast send "$RC" "setAgentInbox(address)" "$INBOX" --rpc-url "$LASNA_RPC_URL" \
  --private-key "$DEPLOYER_PRIVATE_KEY" | tee -a "$LOG"

cat > deployments/m1-addresses.env <<EOF
SIGNAL_SOURCE=$SIGNAL
SENTINEL_REACTIVE=$RC
AGENT_INBOX=$INBOX
EOF
echo "Done. Addresses in deployments/m1-addresses.env"
