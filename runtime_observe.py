from marketmind_engine.state.builder import MarketStateBuilder
from marketmind_engine.adapters.narrative_adapter import NarrativeAdapter
from marketmind_engine.decision.decision_engine import DecisionEngine

from symbol_resolver import SymbolResolver
from price_coupler import PriceCoupler


def main():

    # --- Sample RSS Text (replace with real feed later) ---
    rss_text = """
    Apple AAPL and Tesla TSLA rally after IBM earnings surprise.
    Multiple analysts upgraded Apple following strong AI integration commentary.
    """

    # --- Mock narrative events (simulate RSS timestamps) ---
    from datetime import datetime, timedelta, timezone

    now = datetime.now(timezone.utc)

    rss_events = [
        {"source": "Reuters", "timestamp": now - timedelta(hours=4)},
        {"source": "Bloomberg", "timestamp": now - timedelta(hours=2)},
        {"source": "CNBC", "timestamp": now - timedelta(hours=1)},
    ]

    # --- Build enriched MarketState ---
    builder = MarketStateBuilder(
        narrative_adapter=NarrativeAdapter(),
        symbol_resolver=SymbolResolver(),
        price_adapter=PriceCoupler(),
    )

    raw_inputs = {
        "narrative": rss_events,
        "text": rss_text,
    }

    state = builder.build(raw_inputs)

    # --- Decision Engine ---
    engine = DecisionEngine()
    result = engine.evaluate(state)

    # --- Structured Output ---
    print("\n===== OBSERVE MODE OUTPUT =====\n")
    print("Symbol:", state.symbol)
    print("Price:", state.price)
    print("Price Delta:", state.price_delta)
    print("Volume Ratio:", state.volume_ratio)

    if state.narrative:
        print("\nNarrative Accelerating:", state.narrative.accelerating)
        print("Source Count:", state.narrative.source_count)
        print("Notes:", state.narrative.notes)
    else:
        print("\nNarrative: None")

    print("\nDecision:", result.decision)
    print("\nRule Results:")
    for r in result.rule_results:
        print(" -", r.rule_name, "| Triggered:", r.triggered, "| Block:", r.block, "| Reason:", r.reason)


if __name__ == "__main__":
    main()