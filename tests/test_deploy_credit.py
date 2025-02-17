import brownie
from brownie import Contract
from brownie import config
import math


def test_simple_harvest(
    gov,
    token,
    vault,
    strategist,
    whale,
    strategy,
    chain,
    strategist_ms,
    gauge,
    booster,
    voter,
    rewardsContract,
    amount,
):
    ## deposit to the vault after approving
    startingWhale = token.balanceOf(whale)
    token.approve(vault, 2**256 - 1, {"from": whale})
    vault.deposit(amount, {"from": whale})
    newWhale = token.balanceOf(whale)
    booster.earmarkRewards(strategy.pid(), {"from": strategist})

    # this is part of our check into the staking contract balance
    stakingBeforeHarvest = rewardsContract.balanceOf(strategy)

    # harvest, store asset amount
    chain.sleep(1)
    strategy.harvest({"from": gov})
    chain.sleep(1)
    old_assets = vault.totalAssets()
    assert old_assets > 0
    assert token.balanceOf(strategy) == 0
    assert strategy.estimatedTotalAssets() > 0
    print("\nStarting Assets: ", old_assets / 1e18)

    # try and include custom logic here to check that funds are in the staking contract (if needed)
    assert rewardsContract.balanceOf(strategy) > stakingBeforeHarvest

    # simulate 6 hours of earnings so we don't outrun our convex earmark
    chain.sleep(21600)
    chain.mine(1)

    # harvest, store new asset amount
    chain.sleep(1)
    pending_rewards = strategy.claimableProfitInUsdt()
    assert strategy.stakedBalance() > 0
    assert token.balanceOf(strategy) == 0
    claimable_crv = strategy.claimableBalance()
    assert claimable_crv > 0
    print("\nPending claimable in USDT after 1 day: ", pending_rewards / 1e6)
    strategy.harvest({"from": gov})
    assert strategy.claimableProfitInUsdt() == 0
    chain.sleep(1)
    new_assets = vault.totalAssets()
    # confirm we made money, or at least that we have about the same
    assert new_assets >= old_assets
    print("\nAssets after 1 day: ", new_assets / 1e18)

    # Display estimated APR
    print(
        "\nEstimated DAI APR: ",
        "{:.2%}".format(
            ((new_assets - old_assets) * (365 * 4)) / (strategy.estimatedTotalAssets())
        ),
    )

    ## now we test deploy_credit

    ## deposit to the vault after approving
    vault.deposit(amount, {"from": whale})
    booster.earmarkRewards(strategy.pid(), {"from": strategist})

    # this is part of our check into the staking contract balance
    stakingBeforeDeployCredit = rewardsContract.balanceOf(strategy)
    print("\nBefore deployCredit: ", stakingBeforeDeployCredit / 1e18)

    # harvest, store asset amount
    chain.sleep(1)
    strategy.deployCredit({"from": gov})
    chain.sleep(1)
    old_assets = vault.totalAssets()
    assert old_assets > 0
    assert token.balanceOf(strategy) == 0
    assert strategy.estimatedTotalAssets() > 0

    # try and include custom logic here to check that funds are in the staking contract (if needed)
    print("\nAfter deployCredit: ", rewardsContract.balanceOf(strategy) / 1e18)
    assert rewardsContract.balanceOf(strategy) > stakingBeforeDeployCredit