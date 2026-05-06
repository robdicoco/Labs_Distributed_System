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
        log_.recordDecision("tx-1", CommitLog.Decision.COMMIT);
        assertEq(uint8(log_.getDecision("tx-1")), uint8(CommitLog.Decision.COMMIT));
    }
}
