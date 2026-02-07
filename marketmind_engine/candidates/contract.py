"""
Phase-6A Candidate Output Contract

This module defines the immutable TradeCandidate data structure.
No logic is permitted here.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Literal


@dataclass(frozen=True)
class TradeCandidate:
    """Immutable representation of an intention-supported asset."""

    # Identity
    symbol: str
    domain: str

    # Engine context
    engine_id: str
    engine_time: datetime
    engine_tick: int

    # Intention metrics (projected)
    fils: float
    ucip: float
    ttcf: float

    # Eligibility (observational)
    eligibility_status: bool
    eligibility_reason: str

    # Market confirmation (permission)
    market_confirmation_status: bool
    market_confirmation_reason: str

    # Decision engine output
    decision: Literal["ALLOW", "NO_ACTION"]

    # Narrative snapshot
    narrative_summary: str