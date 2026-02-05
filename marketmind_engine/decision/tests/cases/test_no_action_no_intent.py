"""
Phase-1 negative test: NO_ACTION when intent does NOT trigger.

Verifies that the DecisionEngine does not emit ALLOW_BUY
when NarrativeAcceleration is not triggered.
"""

from marketmind_engine.decision.decision_engine import DecisionEngine
from marketmind_engine.decision.tests.fixtures.market_state_factory import (
    make_market_state,
)


def test_no_action_when_no_intent():
    engine = DecisionEngine()

    # Values chosen to FAIL NarrativeAcceleration
    # while remaining otherwise benign
    state = make_market_state(
        ucip=0.2,
        fils=0.2,
        ttcf=0.1,
    )

    result = engine.evaluate(state)

    # --- Decision assertion ---
    assert result.decision == "NO_ACTION", (
        f"Expected NO_ACTION, got {result.decision}"
    )

    # --- Intent must NOT be triggered ---
    intent_rules = [
        r for r in result.rule_results
        if r.rule_name == "NarrativeAcceleration"
    ]

    assert intent_rules, "NarrativeAcceleration rule did not execute"

    assert intent_rules[0].triggered is False, (
        "Intent rule unexpectedly triggered"
    )