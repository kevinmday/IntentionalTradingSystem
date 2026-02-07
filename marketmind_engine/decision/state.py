"""
MarketState

Canonical immutable state object observed by the DecisionEngine.

MarketState represents *what the engine knows*, not what it does.
"""

from dataclasses import dataclass
from typing import Optional, List


@dataclass(frozen=True)
class MarketState:
    # --------------------------------------------------
    # Core identity
    # --------------------------------------------------
    symbol: Optional[str]
    narrative: Optional[str]

    # --------------------------------------------------
    # Intention fields
    # --------------------------------------------------
    fils: Optional[float]
    ucip: Optional[float]
    ttcf: Optional[float]

    # --------------------------------------------------
    # Structural / fractal context
    # --------------------------------------------------
    fractal_levels: Optional[List[float]]

    # --------------------------------------------------
    # Engine metadata
    # --------------------------------------------------
    data_source: Optional[str]
    engine_id: Optional[str]
    timestamp_utc: Optional[str]

    # --------------------------------------------------
    # Phase-5C: Market capacity (permission only)
    # --------------------------------------------------
    liquidity: Optional[float] = None
    volatility: Optional[float] = None
    responsiveness: Optional[float] = None