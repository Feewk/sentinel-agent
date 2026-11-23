// SPDX-License-Identifier: MIT
pragma solidity ^0.8.29;

import { AbstractReactive } from "@reactive/base/AbstractReactive.sol";
import { ISystemContract } from "@reactive/interfaces/ISystemContract.sol";

/// @title SentinelReactive — Sentinel Agent (Reactive Lasna, chain 5318007)
/// @notice Two-hop reactive brain:
///         Hop 1 — subscribes to SignalSource.Signal on Ethereum Sepolia,
///         triages deterministically (priority only — the DECISION belongs to
///         the off-chain LLM agent), callbacks AgentInbox.recordCase.
///         Hop 2 — subscribes to AgentInbox.DecisionRecorded, callbacks
///         DecisionExecutor.execute so the model's decision lands on-chain.
/// @dev Omni API only. Never revert on non-matching logs: route on topic0,
///      check opCode before decoding data, fall through silently.
///      Payload rule: first argument is address(0), overwritten by the
///      network with this contract's address.
contract SentinelReactive is AbstractReactive {
    uint256 public constant SEPOLIA_CHAIN_ID = 11155111;
    uint64 public constant CALLBACK_GAS_LIMIT = 1_000_000;
    uint256 public constant HIGH_VALUE_THRESHOLD = 500;

    // keccak256("Signal(address,uint256,uint256)")
    uint256 public constant SIGNAL_TOPIC0 =
        uint256(keccak256("Signal(address,uint256,uint256)"));
    // keccak256("DecisionRecorded(uint256,uint8)")
    uint256 public constant DECISION_TOPIC0 =
        uint256(keccak256("DecisionRecorded(uint256,uint8)"));

    address public owner;
    address public signalSource;
    address public agentInbox;
    address public decisionExecutor;

    event InboxSet(address indexed inbox);
    event ExecutorSet(address indexed executor);
    event SignalTriaged(uint256 value, uint256 tag, uint8 priority);
    event DecisionRouted(uint256 caseId, uint8 action);

    error NotOwner();

    modifier onlyOwner() {
        if (msg.sender != owner) revert NotOwner();
        _;
    }

    constructor(address signalSource_) payable {
        owner = msg.sender;
        signalSource = signalSource_;
        SYSTEM.subscribe(
            SEPOLIA_CHAIN_ID,
            signalSource_,
            SIGNAL_TOPIC0,
            REACTIVE_IGNORE,
            REACTIVE_IGNORE,
            REACTIVE_IGNORE
        );
    }

    /// @notice Wire the hop-1 recipient AND subscribe to its DecisionRecorded
    ///         event for hop 2 (the inbox address only exists after the RC,
    ///         per the forced deployment order).
    function setAgentInbox(address inbox_) external onlyOwner {
        agentInbox = inbox_;
        SYSTEM.subscribe(
            SEPOLIA_CHAIN_ID,
            inbox_,
            DECISION_TOPIC0,
            REACTIVE_IGNORE,
            REACTIVE_IGNORE,
            REACTIVE_IGNORE
        );
        emit InboxSet(inbox_);
    }

    function setDecisionExecutor(address executor_) external onlyOwner {
        decisionExecutor = executor_;
        emit ExecutorSet(executor_);
    }

    /// @notice Pay any outstanding debt to the system contract from reserves.
    function coverDebt() external {
        _coverDebt();
    }

    function react(LogRecord calldata log_) external override onlySystem {
        if (log_.topic0 == SIGNAL_TOPIC0) {
            _hop1(log_);
        } else if (log_.topic0 == DECISION_TOPIC0) {
            _hop2(log_);
        }
        // anything else: fall through, never revert
    }

    function _hop1(LogRecord calldata log_) internal {
        if (log_.opCode != 2) return; // Signal: 1 indexed + 2 data params
        if (agentInbox == address(0)) return;

        (uint256 value, uint256 tag) = abi.decode(log_.data, (uint256, uint256));
        uint8 priority = value >= HIGH_VALUE_THRESHOLD ? 1 : 0; // 1 = HIGH
        emit SignalTriaged(value, tag, priority);

        bytes memory payload = abi.encodeWithSignature(
            "recordCase(address,uint256,uint256,uint8)",
            address(0),
            value,
            tag,
            priority
        );
        SYSTEM.requestCallbackV_1_0(
            ISystemContract.CallbackConfiguration_V_1_0({
                chainId: SEPOLIA_CHAIN_ID,
                recipient: agentInbox,
                gasLimit: CALLBACK_GAS_LIMIT,
                payload: payload
            })
        );
    }

    function _hop2(LogRecord calldata log_) internal {
        if (log_.opCode != 2) return; // DecisionRecorded: 1 indexed + 1 data param
        if (decisionExecutor == address(0)) return;

        uint256 caseId = log_.topic1;
        uint8 action = abi.decode(log_.data, (uint8));
        emit DecisionRouted(caseId, action);

        bytes memory payload = abi.encodeWithSignature(
            "execute(address,uint256,uint8)", address(0), caseId, action
        );
        SYSTEM.requestCallbackV_1_0(
            ISystemContract.CallbackConfiguration_V_1_0({
                chainId: SEPOLIA_CHAIN_ID,
                recipient: decisionExecutor,
                gasLimit: CALLBACK_GAS_LIMIT,
                payload: payload
            })
        );
    }
}
