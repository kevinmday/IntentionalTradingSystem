from datetime import datetime, timedelta, timezone

from marketmind_engine.adapters.narrative_adapter import NarrativeAdapter
from marketmind_engine.intelligence.narrative_scoring_engine import NarrativeScoringEngine


def make_event(hours_ago, source):
    return {
        "timestamp": datetime.now(timezone.utc) - timedelta(hours=hours_ago),
        "source": source,
    }


def run_scoring_test():
    print("=== NARRATIVE SCORING TEST ===")

    adapter = NarrativeAdapter()
    scorer = NarrativeScoringEngine()

    raw_events = [
        make_event(5, "Reuters"),
        make_event(1, "Reuters"),
        make_event(1, "AP"),
        make_event(0.5, "Bloomberg"),
    ]

    ctx = adapter.build(raw_events)

    if ctx is None:
        print("No acceleration detected.")
        return

    scores = scorer.score(ctx)

    print("FILS:", scores.fils)
    print("UCIP:", scores.ucip)
    print("TTCF:", scores.ttcf)
    print("Explanation:", scores.explanation)

    print("=== END TEST ===")


if __name__ == "__main__":
    run_scoring_test()