"""
Replay CLI — dry-run / observation only.

Runs a synthetic bar sequence through the engine to:
- exercise adapters
- verify abstention behavior
- log ignition observations

No orders. No execution. No providers.
"""

from datetime import datetime
import pytz

from marketmind_engine.adapters.liquidity_adapter import LiquidityAdapter
from marketmind_engine.decision.decision_engine import DecisionEngine
from marketmind_engine.observers.ignition import FileIgnitionObserver
from marketmind_engine.replay.stub_generator import (
    generate_flat_open,
    generate_ignition_spike,
    chain,
)
from marketmind_engine.replay.replay_runner import run_replay


def main() -> None:
    symbol = "REPLAY_TEST"
    window_size = 20

    # ---- Time anchor (UTC, but open-window aware) ----
    et = pytz.timezone("US/Eastern")
    start_time = et.localize(
        datetime(2026, 2, 6, 9, 30)
    ).astimezone(pytz.UTC)

    # ---- Stub bars ----
    bars = chain(
        generate_flat_open(
            start_time=start_time,
            bars=10,
        ),
        generate_ignition_spike(
            start_time=start_time,
            bars=12,
            spike_multiplier=2.0,
        ),
    )

    # ---- Engine + adapters ----
    observer = FileIgnitionObserver("ignition_replay.jsonl")
    liquidity_adapter = LiquidityAdapter(
        window_size=window_size,
        observer=observer,
    )
    decision_engine = DecisionEngine()

    # ---- Replay ----
    result = run_replay(
        bars=bars,
        liquidity_adapter=liquidity_adapter,
        decision_engine=decision_engine,
        symbol=symbol,
        window_size=window_size,
    )

    # ---- Summary ----
    print("Replay complete.")
    print(f"Bars processed: {len(result.decisions)}")
    print(f"Decisions: {set(result.decisions)}")
    print("Ignition observations written to ignition_replay.jsonl")


if __name__ == "__main__":
    main()