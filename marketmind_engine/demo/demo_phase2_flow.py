from datetime import datetime, timedelta

from marketmind_engine.adapters.narrative_adapter import NarrativeAdapter
from marketmind_engine.state.builder import MarketStateBuilder
from marketmind_engine.decision.decision_engine import DecisionEngine


def make_event(hours_ago, source):
    return {
        "timestamp": datetime.utcnow() - timedelta(hours=hours_ago),
        "source": source,
    }


def run_demo():
    # --- Phase-2 wiring ---
    narrative_adapter = NarrativeAdapter()
    builder = MarketStateBuilder(narrative_adapter=narrative_adapter)

    engine = DecisionEngine()

    # --- Case 1: Narrative acceleration present ---
    accelerating_inputs = {
        "narrative": [
            make_event(5, "Reuters"),
            make_event(1, "Reuters"),
            make_event(1, "AP"),
            make_event(0.5, "Bloomberg"),
        ]
    }

    state = builder.build(accelerating_inputs)
    result = engine.evaluate(state)

    print("\n=== CASE: ACCELERATING NARRATIVE ===")
    print("MarketState:", state)
    print("DecisionResult:", result)

    # --- Case 2: No acceleration ---
    flat_inputs = {
        "narrative": [
            make_event(5, "Reuters"),
            make_event(4, "AP"),
            make_event(1, "Reuters"),
        ]
    }

    state = builder.build(flat_inputs)
    result = engine.evaluate(state)

    print("\n=== CASE: NO ACCELERATION ===")
    print("MarketState:", state)
    print("DecisionResult:", result)


if __name__ == "__main__":
    run_demo()