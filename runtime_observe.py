from marketmind_engine.state.builder import MarketStateBuilder
from marketmind_engine.state.contracts import MarketState
from marketmind_engine.adapters.narrative_adapter import NarrativeAdapter
from marketmind_engine.decision.decision_engine import DecisionEngine

from symbol_resolver import SymbolResolver
from price_coupler import PriceCoupler

import os

IGNITION_TIME_FILE = "ignition_anchor.txt"
IGNITION_PRICE_FILE = "ignition_price.txt"


def main():

    # --- Sample RSS Text ---
    rss_text = """
    Apple AAPL and Tesla TSLA rally after IBM earnings surprise.
    Multiple analysts upgraded Apple following strong AI integration commentary.
    """

    # --- Mock narrative events ---
    from datetime import datetime, timedelta, timezone

    now = datetime.now(timezone.utc)

    rss_events = [
        {"source": "Reuters", "timestamp": now - timedelta(hours=4)},
        {"source": "Bloomberg", "timestamp": now - timedelta(hours=2)},
        {"source": "CNBC", "timestamp": now - timedelta(hours=1)},
    ]

    builder = MarketStateBuilder(
        narrative_adapter=NarrativeAdapter(),
        symbol_resolver=SymbolResolver(),
        price_adapter=PriceCoupler(),
    )

    raw_inputs = {
        "narrative": rss_events,
        "text": rss_text,
    }

    built_state = builder.build(raw_inputs)

    pc = PriceCoupler()
    metrics = pc.get_price_metrics("PLTR")

    engine_time = built_state.engine_time
    current_price = metrics["price"]

    # ============================================================
    # 🔥 IGNITION TIME PERSISTENCE
    # ============================================================

    if os.path.exists(IGNITION_TIME_FILE):
        with open(IGNITION_TIME_FILE, "r") as f:
            ignition_time = int(f.read().strip())
    else:
        ignition_time = engine_time
        with open(IGNITION_TIME_FILE, "w") as f:
            f.write(str(ignition_time))

    # ============================================================
    # 🔥 IGNITION PRICE PERSISTENCE
    # ============================================================

    if os.path.exists(IGNITION_PRICE_FILE):
        with open(IGNITION_PRICE_FILE, "r") as f:
            ignition_price = float(f.read().strip())
    else:
        ignition_price = current_price
        with open(IGNITION_PRICE_FILE, "w") as f:
            f.write(str(ignition_price))

    # --- Calculate ignition-relative delta ---
    delta_since_ignition = (current_price - ignition_price) / ignition_price

    state = MarketState(
        symbol="PLTR",
        domain="equity",
        fils=0.82,
        ucip=0.91,
        ttcf=0.08,
        narrative=built_state.narrative,
        engine_time=engine_time,
        ignition_time=ignition_time,
        volatility=built_state.volatility,
        liquidity=built_state.liquidity,
        price=current_price,
        price_delta=metrics["price_delta"],  # structural 15-min delta
        volume_ratio=metrics["volume_ratio"],
    )

    engine = DecisionEngine()
    result = engine.evaluate(state)

    # ============================================================
    # OUTPUT
    # ============================================================

    print("\n===== LIVE IGNITION TEST (PLTR) =====\n")
    print("Symbol:", state.symbol)
    print("Current Price:", current_price)
    print("Ignition Price:", ignition_price)
    print("Engine Time:", state.engine_time)
    print("Ignition Time:", state.ignition_time)
    print("Latency (s):", state.engine_time - state.ignition_time)

    print("\nDelta Since Ignition:", round(delta_since_ignition, 6))
    print("Structural 15m Delta:", state.price_delta)
    print("Volume Ratio:", state.volume_ratio)

    print("\nFILS:", state.fils)
    print("UCIP:", state.ucip)
    print("TTCF:", state.ttcf)

    print("\nDecision:", result.decision)

    print("\nRule Results:")
    for r in result.rule_results:
        print(" -", r.rule_name, "| Triggered:", r.triggered, "| Block:", r.block, "| Reason:", r.reason)


if __name__ == "__main__":
    main()