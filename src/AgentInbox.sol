// SPDX-License-Identifier: MIT
pragma solidity ^0.8.29;

import { AbstractCallback } from "@reactive/base/AbstractCallback.sol";
import { IPayable } from "@reactive/interfaces/IPayable.sol";

/// @title AgentInbox — Sentinel Agent (Ethereum Sepolia)
/// @notice Destination of hop 1 and origin of hop 2.
///         recordCase: called by SentinelReactive via the Sepolia callback
///         proxy (0xAa14d9Cd0f788Ca23d11805986C1d8bd035D23b4), double-guarded.
///         submitDecision: called only by the off-chain AI agent's EOA after
///         the model decides; emits DecisionRecorded, which SentinelReactive
///         watches for hop 2.
contract AgentInbox is AbstractCallback {
    struct Case {
        uint256 value;
        uint256 tag;
        uint8 priority; // 0 = NORMAL, 1 = HIGH
        bool exists;
        bool decided;
        uint8 action; // 0 = IGNORE, 1 = MONITOR, 2 = ESCALATE
        bytes32 rationaleHash;
    }

    address public owner;
    address public agent;

    uint256 public caseCount;
    mapping(uint256 => Case) public cases;

    event CaseOpened(uint256 indexed caseId, uint256 value, uint256 tag, uint8 priority);
    event DecisionRecorded(uint256 indexed caseId, uint8 action);
    event AgentSet(address indexed agent);

    error NotOwner();
    error NotAgent();
    error UnknownCase(uint256 caseId);
    error AlreadyDecided(uint256 caseId);
    error BadAction(uint8 action);

    constructor(address payable callbackProxy_, address reactive_, address agent_)
        payable
        AbstractCallback(IPayable(callbackProxy_), reactive_)
    {
        owner = msg.sender;
        agent = agent_;
    }

    function setAgent(address agent_) external {
        if (msg.sender != owner) revert NotOwner();
        agent = agent_;
        emit AgentSet(agent_);
    }

    /// @notice Pay any outstanding debt to the callback proxy from reserves.
    function coverDebt() external {
        _coverDebt();
    }

    function recordCase(address reactive_, uint256 value, uint256 tag, uint8 priority)
        external
        onlyServiceProvider
        onlyCallbackSender(reactive_)
    {
        uint256 caseId = ++caseCount;
        cases[caseId] = Case({
            value: value,
            tag: tag,
            priority: priority,
            exists: true,
            decided: false,
            action: 0,
            rationaleHash: bytes32(0)
        });
        emit CaseOpened(caseId, value, tag, priority);
    }

    /// @notice The AI agent's decision entry point. Only the agent EOA.
    function submitDecision(uint256 caseId, uint8 action, bytes32 rationaleHash) external {
        if (msg.sender != agent) revert NotAgent();
        Case storage c = cases[caseId];
        if (!c.exists) revert UnknownCase(caseId);
        if (c.decided) revert AlreadyDecided(caseId);
        if (action > 2) revert BadAction(action);
        c.decided = true;
        c.action = action;
        c.rationaleHash = rationaleHash;
        emit DecisionRecorded(caseId, action);
    }
}
