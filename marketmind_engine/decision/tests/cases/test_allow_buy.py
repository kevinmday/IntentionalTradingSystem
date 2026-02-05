"""
Phase-1 smoke test: ALLOW_BUY path

Verifies that the DecisionEngine emits ALLOW_BUY
when intent is triggered and no blocking rules fire.
"""

from marketmind_engine.decision.decision_engine import DecisionEngine
from marketmind_engine.decision.tests.fixtures.market_state_factory import (
    make_market_state,
)


def test_allow_buy():
    engine = DecisionEngine()

    # Canonical Phase-1 passing state
    state = make_market_state(
        # These values are chosen to:
        # - trigger NarrativeAcceleration
        # - avoid VolatilityCompression
        # - avoid LiquidityParticipation blocks
        ucip=0.8,
        fils=0.85,
        ttcf=0.05,
    )

    result = engine.evaluate(state)

    # --- Decision assertion ---
    assert result.decision == "ALLOW_BUY", (
        f"Expected ALLOW_BUY, got {result.decision}"
    )

    # --- Rule-level assertions ---
    rule_names = [r.rule_name for r in result.rule_results]

    assert "NarrativeAcceleration" in rule_names, (
        "NarrativeAcceleration rule did not execute"
    )

    # Intent must be triggered
    intent_rule = next(
        r for r in result.rule_results
        if r.rule_name == "NarrativeAcceleration"
    )
    assert intent_rule.triggered is True, (
        "Intent rule did not trigger as expected"
    )

    # Blocking rules must NOT trigger
    for r in result.rule_results:
        if r.rule_name in (
            "VolatilityCompression",
            "LiquidityParticipation",
        ):
            assert r.triggered is False, (
                f"Blocking rule {r.rule_name} unexpectedly triggered"
            )