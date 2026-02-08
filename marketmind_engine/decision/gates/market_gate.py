"""
PHASE-6D — MARKET GATE (STUB)

Deterministic market gating logic.
No execution, no capital, no side effects.
"""

from dataclasses import dataclass
from marketmind_engine.decision.state import MarketState


@dataclass(frozen=True)
class MarketGateResult:
    market_confirmed: bool
    reason: str


def evaluate_market_gate(state: MarketState) -> MarketGateResult:
    """
    Phase-6D stub gate.

    Always confirms market.
    Replace with real gating logic in Phase-6D.
    """
    return MarketGateResult(
        market_confirmed=True,
        reason="Phase-6D stub: market confirmed by default",
    )
