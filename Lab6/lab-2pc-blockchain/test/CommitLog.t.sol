// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {CommitLog} from "../src/CommitLog.sol";
import {Test} from "forge-std/Test.sol";

contract CommitLogTest is Test {
    CommitLog internal log_;

    function setUp() public {
        log_ = new CommitLog();
    }

    function testRecordCommit() public {
        log_.recordDecision("tx-1", CommitLog.Decision.COMMIT, 50);
        assertEq(uint8(log_.getDecision("tx-1")), uint8(CommitLog.Decision.COMMIT));

        (
            CommitLog.Decision decision,
            uint256 timestamp,
            address coordinator,
            uint256 amount
        ) = log_.records("tx-1");

        assertEq(uint8(decision), uint8(CommitLog.Decision.COMMIT));
        assertGt(timestamp, 0);
        assertEq(coordinator, address(this));
        assertEq(amount, 50);
    }
}
