from datetime import datetime, timedelta, timezone

from marketmind_engine.adapters.narrative_adapter import NarrativeAdapter
from marketmind_engine.decision.decision_engine import DecisionEngine
from marketmind_engine.decision.state import MarketState


def make_event(hours_ago, source):
    return {
        "timestamp": datetime.now(timezone.utc) - timedelta(hours=hours_ago),
        "source": source,
    }


def run_pipeline_test():
    print("=== RSS → ADAPTER → ENGINE PIPELINE TEST ===")

    adapter = NarrativeAdapter()
    engine = DecisionEngine()

    # ---- Step 1: simulate raw RSS events ----
    raw_events = [
        make_event(5, "Reuters"),
        make_event(1, "Reuters"),
        make_event(1, "AP"),
        make_event(0.5, "Bloomberg"),
    ]

    # ---- Step 2: adapter builds narrative context ----
    ctx = adapter.build(raw_events)

    if ctx is None:
        print("NarrativeAdapter returned None (no acceleration)")
        return

    print(f"Narrative accelerating: {ctx.accelerating}")
    print(f"Source count: {ctx.source_count}")
    print(f"Notes: {ctx.notes}")

    # ---- Step 3: synthesize MarketState from context ----
    # Here we simulate a mapping from narrative strength → FILS/UCIP
    # (in live system this will come from scoring engine)

    state = MarketState(
        symbol="TEST",
        domain="ai",
        narrative="Synthetic RSS ignition",
        fils=0.88,
        ucip=0.91,
        ttcf=0.06,
        fractal_levels=None,
        data_source="rss-pipeline-sim",
        engine_id="rss-pipeline",
        timestamp_utc=datetime.now(timezone.utc),
        engine_time=100,
        ignition_time=100,
        price_delta=0.01,
        volume_ratio=2.3,
    )

    result = engine.evaluate(state)

    print(f"Decision: {result.decision}")
    print("=== END TEST ===")


if __name__ == "__main__":
    run_pipeline_test()