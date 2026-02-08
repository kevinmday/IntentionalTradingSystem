"""
PHASE-6D CONTRACT TEST — MARKET GATING (STUB)

Tests deterministic market gating behavior.
"""

from marketmind_engine.decision.gates.market_gate import evaluate_market_gate
from marketmind_engine.decision.tests.fixtures.market_state_factory import (
    make_market_state,
)


def test_phase6d_market_gate_stub_is_deterministic():
    state = make_market_state(symbol="TEST", domain="TEST")

    result1 = evaluate_market_gate(state)
    result2 = evaluate_market_gate(state)

    assert result1 == result2
    assert result1.market_confirmed is True
    assert isinstance(result1.reason, str)
