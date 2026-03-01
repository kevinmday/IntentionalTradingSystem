"""
Open Session Replay Harness
Deterministic Signal Activation Layer

Simulates first 20 minutes of a trading session.
Clock + Price + Policy injection enabled.
No server required.
"""

from marketmind_engine.runtime.build_engine import build_engine
from marketmind_engine.replay.replay_clock import ReplayClock
from marketmind_engine.replay.historical_price_feed import HistoricalPriceFeed
from marketmind_engine.replay.synthetic_policy_engine import (
    SyntheticMomentumPolicy,
)


def run_replay():

    print("Starting replay...")

    replay_clock = ReplayClock(start_time=0)
    price_feed = HistoricalPriceFeed(replay_clock)
    policy_engine = SyntheticMomentumPolicy()

    engine_controller = build_engine(
        clock=replay_clock,
        price_service=price_feed,
        policy_engine=policy_engine,
    )

    engine_controller.start()

    for minute in range(20):

        current_time = replay_clock.now()
        current_price = price_feed.get_price("TEST")

        print(
            f"Minute {minute:02d} | "
            f"t={current_time:>4} | "
            f"price={current_price:.2f}"
        )

        result = engine_controller.run_symbol_cycle("TEST")

        print("  Decision:", result.get("decision"))
        print("  Intent:", result.get("order_intent"))
        print("  Receipt:", result.get("execution_receipt"))
        print("--------------------------------------------------")

        replay_clock.advance(60)

    print("Replay complete.")


if __name__ == "__main__":
    run_replay()