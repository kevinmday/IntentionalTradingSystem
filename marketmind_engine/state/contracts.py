from dataclasses import dataclass
from typing import Optional

from marketmind_engine.adapters.contracts import NarrativeContext


@dataclass(frozen=True)
class MarketState:
    """
    Canonical immutable market state used by DecisionEngine.

    This must satisfy ALL rule dependencies.
    """

    # --- Identity ---
    symbol: Optional[str] = None
    domain: Optional[str] = None

    # --- Intention Field Metrics ---
    fils: float = 0.0
    ucip: float = 0.0
    ttcf: float = 0.0

    # --- Narrative ---
    narrative: Optional[NarrativeContext] = None

    # --- Timing ---
    engine_time: Optional[int] = None
    ignition_time: Optional[int] = None

    # --- Macro ---
    volatility: Optional[object] = None
    liquidity: Optional[object] = None

    # --- Price Coupling ---
    price: Optional[float] = None
    price_delta: float = 0.0
    volume_ratio: float = 1.0

    # --- Derived Signal Metrics ---
    drift: float = 0.0
    delta_since_ignition: float = 0.0
