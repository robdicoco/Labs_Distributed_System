// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {Script, console} from "forge-std/Script.sol";
import {CommitLog} from "../src/CommitLog.sol";

/// @dev For local/anvil simulation only. Production deploy uses deploy/index.html + MetaMask.
contract DeployScript is Script {
    function run() external {
        vm.startBroadcast();
        CommitLog deployed = new CommitLog();
        console.log("CommitLog deployed at:", address(deployed));
        vm.stopBroadcast();
    }
}
