"""
Phase-2 End-to-End Smoke Test

Validates:
- NarrativeAdapter (real event-based API)
- VolatilityAdapter
- LiquidityAdapter
- MarketStateBuilder
- DecisionEngine

This is NOT a unit test.
This is a behavioral wiring test.
"""

from datetime import datetime, timedelta

from marketmind_engine.adapters.narrative_adapter import NarrativeAdapter
from marketmind_engine.adapters.volatility_adapter import VolatilityAdapter
from marketmind_engine.adapters.liquidity_adapter import LiquidityAdapter
from marketmind_engine.state.builder import MarketStateBuilder
from marketmind_engine.decision.decision_engine import DecisionEngine


def main():
    now = datetime.utcnow()

    # --- Adapters (real APIs, no assumptions) ---
    narrative_adapter = NarrativeAdapter()
    volatility_adapter = VolatilityAdapter()
    liquidity_adapter = LiquidityAdapter()

    # --- Builder ---
    builder = MarketStateBuilder(
        narrative_adapter=narrative_adapter,
        volatility_adapter=volatility_adapter,
        liquidity_adapter=liquidity_adapter,
    )

    engine = DecisionEngine()

    # ==================================================
    # CASE 1: Narrative acceleration, weak liquidity
    # ==================================================
    raw_inputs = {
        "narrative": [
            {"source": "Reuters", "timestamp": now - timedelta(hours=5)},
            {"source": "Bloomberg", "timestamp": now - timedelta(hours=4)},
            {"source": "Reuters", "timestamp": now - timedelta(hours=1)},
        ],
        "volatility": [1.5, 1.4, 1.3, 1.2, 1.1],
        "liquidity": {
            "volume_series": [100, 102, 101, 103, 104],
            "trade_count_series": [50, 51, 52, 51, 52],
        },
    }

    state = builder.build(raw_inputs)
    decision = engine.evaluate(state)

    print("\nCASE 1 — Narrative accel, weak liquidity")
    print("Expected: NO_ACTION")
    print("Actual:  ", decision.decision)

    # ==================================================
    # CASE 2: All three axes aligned
    # ==================================================
    raw_inputs["liquidity"] = {
        "volume_series": [100, 105, 110, 115, 200],
        "trade_count_series": [50, 52, 53, 55, 90],
    }

    state = builder.build(raw_inputs)
    decision = engine.evaluate(state)

    print("\nCASE 2 — All axes aligned")
    print("Expected: ALLOW_BUY")
    print("Actual:  ", decision.decision)

    # ==================================================
    # CASE 3: Missing narrative
    # ==================================================
    raw_inputs["narrative"] = None

    state = builder.build(raw_inputs)
    decision = engine.evaluate(state)

    print("\nCASE 3 — Missing narrative")
    print("Expected: NO_ACTION")
    print("Actual:  ", decision.decision)


if __name__ == "__main__":
    main()