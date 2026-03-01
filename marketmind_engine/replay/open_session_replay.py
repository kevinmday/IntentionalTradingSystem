"""
Open Session Replay Harness
Deterministic Signal Activation Layer

Simulates first 20 minutes of a trading session.
Clock + Price + Policy injection enabled.
Position-aware.
Exit-aware.
No server required.
"""

from marketmind_engine.runtime.build_engine import build_engine
from marketmind_engine.replay.replay_clock import ReplayClock
from marketmind_engine.replay.historical_price_feed import HistoricalPriceFeed
from marketmind_engine.replay.synthetic_policy_engine import (
    SyntheticMomentumPolicy,
)
from marketmind_engine.replay.replay_position_service import (
    ReplayPositionService,
)


def run_replay():

    print("Starting replay...")

    # --------------------------------------------------
    # Deterministic Components
    # --------------------------------------------------

    replay_clock = ReplayClock(start_time=0)
    price_feed = HistoricalPriceFeed(replay_clock)
    policy_engine = SyntheticMomentumPolicy()

    # Replay-only position tracker
    position_service = ReplayPositionService()

    # --------------------------------------------------
    # Engine Build (Injection-Capable)
    # --------------------------------------------------

    engine_controller = build_engine(
        clock=replay_clock,
        price_service=price_feed,
        policy_engine=policy_engine,
        position_service=position_service,
    )

    engine_controller.start()

    # --------------------------------------------------
    # 20 Minute Simulation
    # --------------------------------------------------

    for minute in range(20):

        current_time = replay_clock.now()
        current_price = price_feed.get_price("TEST")

        print(
            f"Minute {minute:02d} | "
            f"t={current_time:>4} | "
            f"price={current_price:.2f}"
        )

        # --------------------------------------------------
        # Build Lifecycle Market Context (EXIT FEED)
        # --------------------------------------------------

        market_context_map = {
            "TEST": {
                "price": current_price,
                "fils": 0.0,
                "ttcf": 0.0,
                "drift": 0.0,
            }
        }

        result = engine_controller.run_symbol_cycle(
            "TEST",
            market_context_map=market_context_map,
        )

        decision = result.get("decision")
        intent = result.get("order_intent")
        receipt = result.get("execution_receipt")

        print("  Decision:", decision)
        print("  Intent:", intent)
        print("  Receipt:", receipt)

        # --------------------------------------------------
        # Apply Fill → Update Replay Position State
        # --------------------------------------------------

        if receipt and receipt.accepted and intent:
            position_service.apply_fill(
                symbol=intent.symbol,
                side=intent.side,
                quantity=intent.quantity,
                price=current_price,
            )

        print("--------------------------------------------------")

        replay_clock.advance(60)

    print("Replay complete.")


if __name__ == "__main__":
    run_replay()