"""
Phase-1 smoke test: ALLOW_BUY path

⚠ LEGACY TEST — PHASE-1 ONLY

This test validates Phase-1 DecisionEngine behavior where
intent alone could emit ALLOW_BUY.

As of Phase-6, trade decisions REQUIRE explicit gate approval
(e.g. MarketGate, LiquidityGate, PolicyGate).

This test is intentionally skipped to preserve historical
correctness without corrupting Phase-6 semantics.
"""

import pytest

pytest.skip(
    "Phase-1 legacy test — Phase-6 decision requires explicit gate approval",
    allow_module_level=True,
)

# -------------------------------------------------------------------
# Original Phase-1 test preserved below for reference only
# -------------------------------------------------------------------

from marketmind_engine.decision.decision_engine import DecisionEngine
from marketmind_engine.decision.tests.fixtures.market_state_factory import (
    make_market_state,
)


def test_allow_buy():
    engine = DecisionEngine()

    state = make_market_state(
        ucip=0.8,
        fils=0.85,
        ttcf=0.05,
    )

    result = engine.evaluate(state)

    assert result.decision == "ALLOW_BUY"