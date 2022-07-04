// SPDX-License-Identifier: AGPL-3.0
pragma solidity 0.6.12;

interface IStrategy {
    function harvest() external;
    function deployCredit() external;
}

contract KeeperWrapper {
    function harvestStrategy(address _strategy) external {
        IStrategy(_strategy).harvest();
    }
    function deployCredit(address _strategy) external {
        IStrategy(_strategy).deployCredit();
    }
}