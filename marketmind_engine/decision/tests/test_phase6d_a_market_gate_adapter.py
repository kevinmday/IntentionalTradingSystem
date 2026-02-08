"""
PHASE-6D-A CONTRACT TEST — MARKET GATE ADAPTER

Ensures adapter wiring is deterministic and transparent.
"""

from marketmind_engine.decision.adapters.market_gate_adapter import run_market_gate
from marketmind_engine.decision.tests.fixtures.market_state_factory import (
    make_market_state,
)


def test_phase6d_a_market_gate_adapter_is_deterministic():
    state = make_market_state(symbol="TEST", domain="TEST")

    r1 = run_market_gate(state)
    r2 = run_market_gate(state)

    assert r1 == r2
    assert r1.market_confirmed is True
    assert isinstance(r1.reason, str)
