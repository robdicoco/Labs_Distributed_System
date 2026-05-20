// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

contract CommitLog {
    enum Decision {
        UNKNOWN,
        COMMIT,
        ABORT
    }

    struct TransactionRecord {
        Decision decision;
        uint256 timestamp;
        address coordinator;
        uint256 amount;
    }

    mapping(string => TransactionRecord) public records;

    event DecisionRecorded(
        string indexed transactionId,
        Decision decision,
        uint256 timestamp,
        address coordinator,
        uint256 amount
    );

    function recordDecision(
        string memory transactionId,
        Decision decision,
        uint256 amount
    ) public {
        require(
            records[transactionId].decision == Decision.UNKNOWN,
            "Decision already recorded"
        );

        require(
            decision == Decision.COMMIT || decision == Decision.ABORT,
            "Invalid decision"
        );

        require(amount > 0, "Invalid amount");

        records[transactionId] = TransactionRecord({
            decision: decision,
            timestamp: block.timestamp,
            coordinator: msg.sender,
            amount: amount
        });

        emit DecisionRecorded(
            transactionId, decision, block.timestamp, msg.sender, amount
        );
    }

    function getDecision(string memory transactionId) public view returns (Decision) {
        return records[transactionId].decision;
    }
}
