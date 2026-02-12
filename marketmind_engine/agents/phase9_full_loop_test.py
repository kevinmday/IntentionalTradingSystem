"""
Phase 9.2 — Full Exit Loop Integration Test

Validates:

1. PortfolioManager opens position
2. LifecycleManager creates agent
3. Agent emits EXIT signal
4. PortfolioManager closes position
5. Capital mutates correctly
6. LifecycleManager removes agent
"""

from marketmind_engine.agents.lifecycle_manager import AgentLifecycleManager
from marketmind_engine.execution.position import Position
from marketmind_engine.execution.position_snapshot import PositionSnapshot
from marketmind_engine.execution.capital_snapshot import CapitalSnapshot
from portfolio.portfolio_manager import PortfolioManager


def run_full_loop_test():
    print("\n--- PHASE 9.2 FULL LOOP TEST ---")

    # -------------------------------------------------
    # 1. Create initial capital
    # -------------------------------------------------
    initial_capital = CapitalSnapshot(
        account_equity=100000.0,
        buying_power=100000.0,
        cash=100000.0,
        total_exposure=0.0,
        max_risk_per_trade=0.02,
        open_positions_count=0,
        margin_enabled=False,
    )

    portfolio = PortfolioManager(initial_capital)

    # -------------------------------------------------
    # 2. Simulate opening a position manually
    # -------------------------------------------------
    open_position = Position(
        symbol="AAPL",
        quantity=100,
        average_entry_price=100.0,
        market_value=10000.0,
        unrealized_pnl=0.0,
        side="long",
    )

    # Inject position directly (simulate post-fill state)
    portfolio._positions["AAPL"] = open_position

    # Update capital exposure
    portfolio._capital = CapitalSnapshot(
        account_equity=100000.0,
        buying_power=90000.0,
        cash=90000.0,
        total_exposure=10000.0,
        max_risk_per_trade=0.02,
        open_positions_count=1,
        margin_enabled=False,
    )

    # -------------------------------------------------
    # 3. Sync lifecycle
    # -------------------------------------------------
    lifecycle = AgentLifecycleManager()
    snapshot = portfolio.position_snapshot()
    lifecycle.sync_with_portfolio(snapshot)

    print("Active agents after open:", lifecycle.active_symbols())
    assert lifecycle.active_symbols() == ["AAPL"]

    # -------------------------------------------------
    # 4. Force TTCF inversion → EXIT
    # -------------------------------------------------
    market_context = {
        "AAPL": {
            "price": 110.0,  # profitable exit
            "fils": 75,
            "ttcf": 0.30,  # inversion trigger
            "drift": 0.02,
        }
    }

    signals = lifecycle.evaluate_all(market_context)
    exit_signal = signals[0]

    assert exit_signal.action == "EXIT"
    print("Agent emitted EXIT")

    # -------------------------------------------------
    # 5. Close position via PortfolioManager
    # -------------------------------------------------
    portfolio.close_position("AAPL", price=110.0)

    # -------------------------------------------------
    # 6. Resync lifecycle after close
    # -------------------------------------------------
    snapshot_after = portfolio.position_snapshot()
    lifecycle.sync_with_portfolio(snapshot_after)

    print("Active agents after close:", lifecycle.active_symbols())

    # -------------------------------------------------
    # 7. Validate results
    # -------------------------------------------------
    assert lifecycle.active_symbols() == []
    assert portfolio.position_snapshot().positions == {}

    final_capital = portfolio.capital_snapshot()

    print("Final cash:", final_capital.cash)
    print("Final equity:", final_capital.account_equity)

    # Profit = (110 - 100) * 100 = 1000
    assert final_capital.cash == 101000.0
    assert final_capital.account_equity == 101000.0

    print("\nPhase 9.2 Full Loop: PASS")


if __name__ == "__main__":
    run_full_loop_test()