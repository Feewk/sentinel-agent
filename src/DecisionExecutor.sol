// SPDX-License-Identifier: MIT
pragma solidity ^0.8.29;

import { AbstractCallback } from "@reactive/base/AbstractCallback.sol";
import { IPayable } from "@reactive/interfaces/IPayable.sol";

/// @title DecisionExecutor — Sentinel Agent (Ethereum Sepolia)
/// @notice Destination of hop 2. Receives the AI agent's decision from
///         SentinelReactive via the Sepolia callback proxy and executes it
///         on-chain: per-action counters are the visible state consequence.
/// @dev Double-guarded like AgentInbox: onlyServiceProvider (the proxy) AND
///      onlyCallbackSender (first payload address is SentinelReactive).
contract DecisionExecutor is AbstractCallback {
    // action: 0 = IGNORE, 1 = MONITOR, 2 = ESCALATE
    uint256[3] public actionCounts;
    uint256 public totalExecuted;

    event ActionExecuted(uint256 indexed caseId, uint8 action);

    constructor(address payable callbackProxy_, address reactive_)
        payable
        AbstractCallback(IPayable(callbackProxy_), reactive_)
    {}

    /// @notice Pay any outstanding debt to the callback proxy from reserves.
    function coverDebt() external {
        _coverDebt();
    }

    function execute(address reactive_, uint256 caseId, uint8 action)
        external
        onlyServiceProvider
        onlyCallbackSender(reactive_)
    {
        require(action <= 2, "bad action");
        actionCounts[action] += 1;
        totalExecuted += 1;
        emit ActionExecuted(caseId, action);
    }
}
