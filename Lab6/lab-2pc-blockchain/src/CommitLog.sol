// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

contract CommitLog {
    enum Decision {
        UNKNOWN,
        COMMIT,
        ABORT
    }

    struct TransactionRecord {
        string transactionId;
        Decision decision;
        uint256 timestamp;
        address coordinator;
    }

    mapping(string => TransactionRecord) public records;

    event DecisionRecorded(
        string transactionId,
        Decision decision,
        uint256 timestamp,
        address coordinator
    );

    function recordDecision(string memory transactionId, Decision decision) public {
        require(
            records[transactionId].decision == Decision.UNKNOWN,
            "Decision already recorded"
        );

        require(
            decision == Decision.COMMIT || decision == Decision.ABORT,
            "Invalid decision"
        );

        records[transactionId] = TransactionRecord({
            transactionId: transactionId,
            decision: decision,
            timestamp: block.timestamp,
            coordinator: msg.sender
        });

        emit DecisionRecorded(transactionId, decision, block.timestamp, msg.sender);
    }

    function getDecision(string memory transactionId) public view returns (Decision) {
        return records[transactionId].decision;
    }
}
