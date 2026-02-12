from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class AgentSignal:
    """
    Immutable signal emitted by a PositionAgent.
    Does not mutate state.
    Does not execute trades.
    Pure intent.
    """

    symbol: str
    action: str  # "HOLD" | "EXIT"
    reason: str
    confidence: float  # 0.0 → 1.0
    stop_price: Optional[float] = None