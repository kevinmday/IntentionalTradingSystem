from datetime import datetime, timedelta, timezone

from marketmind_engine.adapters.narrative_adapter import NarrativeAdapter
from marketmind_engine.intelligence.narrative_scoring_engine import NarrativeScoringEngine
from marketmind_engine.decision.decision_engine import DecisionEngine
from marketmind_engine.decision.state import MarketState


def make_event(hours_ago, source):
    return {
        "timestamp": datetime.now(timezone.utc) - timedelta(hours=hours_ago),
        "source": source,
    }


def run_pipeline_test():
    print("=== RSS → ADAPTER → SCORER → ENGINE PIPELINE TEST ===")

    adapter = NarrativeAdapter()
    scorer = NarrativeScoringEngine()
    engine = DecisionEngine()

    # ---- Step 1: simulate raw RSS events ----
    raw_events = [
        make_event(5, "Reuters"),
        make_event(1, "Reuters"),
        make_event(1, "AP"),
        make_event(0.5, "Bloomberg"),
    ]

    # ---- Step 2: build narrative context ----
    ctx = adapter.build(raw_events)

    if ctx is None:
        print("NarrativeAdapter returned None (no acceleration)")
        return

    print(f"Narrative accelerating: {ctx.accelerating}")
    print(f"Source count: {ctx.source_count}")
    print(f"Notes: {ctx.notes}")

    # ---- Step 3: score narrative deterministically ----
    scores = scorer.score(ctx)

    if scores is None:
        print("Scoring engine returned None.")
        return

    print("FILS:", scores.fils)
    print("UCIP:", scores.ucip)
    print("TTCF:", scores.ttcf)
    print("Explanation:", scores.explanation)

    # ---- Step 4: construct MarketState from scores ----
    state = MarketState(
        symbol="TEST",
        domain="ai",
        narrative="Synthetic RSS ignition",
        fils=scores.fils,
        ucip=scores.ucip,
        ttcf=scores.ttcf,
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