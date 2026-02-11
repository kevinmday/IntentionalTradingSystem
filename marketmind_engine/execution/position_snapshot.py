from dataclasses import dataclass
from typing import Dict

from .position import Position


@dataclass(frozen=True)
class PositionSnapshot:
    """
    Immutable portfolio position state.

    Provided to ExecutionEngine to enforce exposure limits,
    position concentration, and duplicate symbol prevention.
    """

    positions: Dict[str, Position]

    total_market_value: float
    total_unrealized_pnl: float
