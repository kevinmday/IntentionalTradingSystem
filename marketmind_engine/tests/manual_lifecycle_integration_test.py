"""
Manual Lifecycle Integration Test — HOLD Variant

Verifies:

1. No exit condition breached
2. Agent emits HOLD
3. Deterministic non-exit behavior

Run with:

python -m marketmind_engine.tests.manual_lifecycle_integration_test
"""

from marketmind_engine.execution.position import Position
from marketmind_engine.execution.position_snapshot import PositionSnapshot
from marketmind_engine.agents.lifecycle_manager import AgentLifecycleManager


def main():

    print("=== Manual Lifecycle Integration Test — HOLD ===")

    # -------------------------------------------------
    # Create a test position
    # -------------------------------------------------

    position = Position(
        symbol="AAPL",
        quantity=10,
        average_entry_price=100.0,
        market_value=1000.0,
        unrealized_pnl=0.0,
        side="long",
    )

    snapshot = PositionSnapshot(
        positions={"AAPL": position},
        total_market_value=1000.0,
        total_unrealized_pnl=0.0,
    )

    manager = AgentLifecycleManager()
    manager.sync_with_portfolio(snapshot)

    print("Active agents:", manager.active_symbols())

    # -------------------------------------------------
    # Market context triggering HOLD
    # All metrics stable
    # -------------------------------------------------

    market_context = {
        "AAPL": {
            "price": 102.0,    # above entry
            "fils": 75,        # strong narrative
            "ttcf": 0.05,      # stable chaos
            "drift": 0.02,     # positive drift
        }
    }

    signals = manager.evaluate_all(market_context)

    for signal in signals:
        print("Signal:", signal.symbol, signal.action, signal.reason)

    # -------------------------------------------------
    # Assertions
    # -------------------------------------------------

    assert len(signals) == 1
    assert signals[0].action == "HOLD"
    assert signals[0].reason == "Conditions stable"

    print("HOLD logic verified.")
    print("=== TEST COMPLETE ===")


if __name__ == "__main__":
    main()