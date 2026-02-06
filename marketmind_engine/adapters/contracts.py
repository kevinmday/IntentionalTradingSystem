from dataclasses import dataclass
from typing import Optional, Dict


# =====================================================
# Narrative Axis
# =====================================================

@dataclass(frozen=True)
class NarrativeContext:
    """
    Interpretive judgment about narrative acceleration.
    Kernel-relevant field: accelerating
    """
    accelerating: bool
    source_count: int
    window: str
    notes: Optional[str] = None

    # Phase-1 compatibility (legacy rule expectations)
    mentions_current: int = 0
    mentions_prior: int = 0
    mentions_previous: int = 0


# =====================================================
# Volatility Axis
# =====================================================

@dataclass(frozen=True)
class VolatilityContext:
    """
    Interpretive judgment about volatility regime.
    Kernel-relevant field: compressed
    """
    compressed: bool
    window: str
    metric: str
    metadata: Dict


# =====================================================
# Liquidity Axis
# =====================================================

@dataclass(frozen=True)
class LiquidityContext:
    """
    Interpretive judgment about participation reality.
    Kernel-relevant field: participating
    """
    participating: bool
    window: str
    metric: str
    metadata: Dict