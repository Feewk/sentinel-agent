// SPDX-License-Identifier: MIT
pragma solidity ^0.8.29;

/// @title SignalSource — Sentinel Agent (M1, hop-1 origin, Ethereum Sepolia)
/// @notice Plain event producer. Emits Signal; SentinelReactive (Lasna)
///         subscribes to topic0 with topic1 = sender, value+tag in data.
///         Design per REACTIVE-BUILD-PLAN.md §c: 1 indexed param + 2 data
///         params, so LogRecord.opCode == 2 for this event.
contract SignalSource {
    event Signal(address indexed sender, uint256 value, uint256 tag);

    uint256 public signalCount;

    function emitSignal(uint256 value, uint256 tag) external {
        signalCount += 1;
        emit Signal(msg.sender, value, tag);
    }
}
