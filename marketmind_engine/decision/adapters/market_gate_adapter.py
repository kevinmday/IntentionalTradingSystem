"""
PHASE-6D-A — MARKET GATE ADAPTER (STUB)

Purpose:
- Isolate DecisionEngine from gate implementations
- Preserve deterministic, testable boundaries
"""

from marketmind_engine.decision.state import MarketState
from marketmind_engine.decision.gates.market_gate import (
    evaluate_market_gate,
    MarketGateResult,
)


def run_market_gate(state: MarketState) -> MarketGateResult:
    """
    Adapter wrapper for market gating.

    Phase-6D-A:
    - Pass-through only
    - No policy, no branching
    """
    return evaluate_market_gate(state)
