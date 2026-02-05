"""
Phase-1 Decision Engine Smoke Test

Validates deterministic behavior of the Phase-1 decision kernel
using minimal, explicit inputs.
"""

from types import SimpleNamespace

from marketmind_engine.decision.decision_engine import DecisionEngine
from marketmind_engine.decision.tests.fixtures.market_state_factory import (
    make_market_state,
)


def run_case(label: str, state):
    print(f"\n--- CASE: {label} ---")
    engine = DecisionEngine()
    result = engine.evaluate(state)

    print(f"Decision: {result.decision}")
    print(f"Triggered rules: {result.triggered_rules}")
    print(f"Blocked rules: {result.blocked_rules}")

    return result


def main():
    print("=" * 44)
    print("Phase-1 Decision Engine Smoke Test")
    print("=" * 44)

    # --------------------------------------------------
    # CASE 1: ALLOW_BUY (intent present, no blocks)
    # --------------------------------------------------
    narrative_stub = SimpleNamespace(
        mentions_current=5,
        mentions_previous=2,
        source_count=3,
    )

    r1 = run_case(
        "ALLOW_BUY (intent present, no blocks)",
        make_market_state(
            narrative=narrative_stub,
            ucip=0.8,
            fils=0.85,
            ttcf=0.05,
        ),
    )

    assert r1.decision == "ALLOW_BUY"

    # --------------------------------------------------
    # CASE 2: NO_ACTION (no intent)
    # --------------------------------------------------
    r2 = run_case(
        "NO_ACTION (no intent)",
        make_market_state(
            ucip=0.2,
            fils=0.2,
            ttcf=0.1,
        ),
    )

    assert r2.decision == "NO_ACTION"

    print("\n✅ Phase-1 smoke test PASSED")


if __name__ == "__main__":
    main()