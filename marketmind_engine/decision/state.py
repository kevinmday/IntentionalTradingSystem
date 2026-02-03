"""
Decision State Object

Defines the canonical snapshot structure consumed by
decision rules and policies within MarketMind.
"""

from dataclasses import dataclass
from typing import List, Optional


@dataclass(frozen=True)
class MarketState:
    """
    Immutable snapshot of analyzed market intention state.
    """

    # --- Core intention metrics ---
    ucip: float
    fils: float
    ttcf: float

    # --- Optional derived structures ---
    fractal_levels: Optional[List[float]] = None

    # --- Contextual metadata ---
    symbol: Optional[str] = None
    data_source: Optional[str] = None
    engine_id: Optional[str] = None
    timestamp_utc: Optional[str] = None
