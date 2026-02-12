"""
Phase 9 Smoke Test

Validates:
- PositionAgent exit logic
- AgentLifecycleManager sync
- EXIT signal emission on TTCF inversion
"""

from marketmind_engine.agents.lifecycle_manager import AgentLifecycleManager
from marketmind_engine.execution.position import Position
from marketmind_engine.execution.position_snapshot import PositionSnapshot


def run_smoke_test():
    print("\n--- PHASE 9 SMOKE TEST ---")

    # ----------------------------------------
    # 1. Create fake open position
    # ----------------------------------------
    position = Position(
        symbol="AAPL",
        quantity=100,
        average_entry_price=100.0,
        market_value=10000.0,
        unrealized_pnl=0.0,
        side="long",
    )

    snapshot = PositionSnapshot(
        positions={"AAPL": position},
        total_market_value=10000.0,
        total_unrealized_pnl=0.0,
    )

    # ----------------------------------------
    # 2. Sync lifecycle manager
    # ----------------------------------------
    lifecycle = AgentLifecycleManager()
    lifecycle.sync_with_portfolio(snapshot)

    print("Active agents:", lifecycle.active_symbols())

    # ----------------------------------------
    # 3. Force TTCF inversion
    # ----------------------------------------
    market_context = {
        "AAPL": {
            "price": 102.0,
            "fils": 75,
            "ttcf": 0.25,  # inversion trigger
            "drift": 0.01,
        }
    }

    signals = lifecycle.evaluate_all(market_context)

    # ----------------------------------------
    # 4. Inspect signal
    # ----------------------------------------
    for signal in signals:
        print("Signal:")
        print("  Symbol:", signal.symbol)
        print("  Action:", signal.action)
        print("  Reason:", signal.reason)
        print("  Confidence:", signal.confidence)

        assert signal.action == "EXIT"
        assert signal.reason == "TTCF inversion"

    print("\nPhase 9 Agent Layer: PASS")


if __name__ == "__main__":
    run_smoke_test()