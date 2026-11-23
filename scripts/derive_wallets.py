#!/usr/bin/env python3
"""Derive Sentinel Agent wallets from the Mr. X agent seed.

Reads ~/.mr-x-wallet/wallet-seed.json, derives:
  deployer: m/44'/60'/0'/0/0  (must equal the known Mr. X EVM address)
  agent:    m/44'/60'/0'/0/1  (separate EOA for submitDecision)
Writes keys ONLY into ../.env (mode 600). Prints addresses only — never keys.
"""
import json
import os
import sys

sys.path.insert(0, os.path.expanduser("~/workspace/theta-hackathon/.venv/lib"))
from eth_account import Account

Account.enable_unaudited_hdwallet_features()

SEED_FILE = os.path.expanduser("~/.mr-x-wallet/wallet-seed.json")
ENV_FILE = os.path.join(os.path.dirname(__file__), "..", ".env")
EXPECTED_DEPLOYER = "0xd225DC890959c52ae92D9264e98eb17dFe9bD46F"


def main() -> None:
    with open(SEED_FILE) as f:
        seed = json.load(f)
    mnemonic = seed["mnemonic"]

    deployer = Account.from_mnemonic(mnemonic, account_path="m/44'/60'/0'/0/0")
    agent = Account.from_mnemonic(mnemonic, account_path="m/44'/60'/0'/0/1")

    if deployer.address.lower() != EXPECTED_DEPLOYER.lower():
        raise SystemExit(f"ABORT: derived deployer {deployer.address} != expected {EXPECTED_DEPLOYER}")

    lines = [
        "SEPOLIA_RPC_URL=https://ethereum-sepolia-rpc.publicnode.com",
        "LASNA_RPC_URL=https://lasna-rpc.rnk.dev/",
        f"DEPLOYER_ADDRESS={deployer.address}",
        f"DEPLOYER_PRIVATE_KEY={deployer.key.hex()}",
        f"AGENT_ADDRESS={agent.address}",
        f"AGENT_PRIVATE_KEY={agent.key.hex()}",
    ]
    fd = os.open(ENV_FILE, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w") as f:
        f.write("\n".join(lines) + "\n")
    os.chmod(ENV_FILE, 0o600)

    print(f"deployer: {deployer.address} (verified against known Mr. X EVM address)")
    print(f"agent:    {agent.address}")
    print(f".env written to {os.path.abspath(ENV_FILE)} with mode 600; keys not printed")


if __name__ == "__main__":
    main()
