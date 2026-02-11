from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from marketmind_engine.policy.policy_result import PolicyResult
from marketmind_engine.decision.state import MarketState
from marketmind_engine.execution.capital_snapshot import CapitalSnapshot
from marketmind_engine.execution.position_snapshot import PositionSnapshot


@dataclass(frozen=True)
class ExecutionInput:
    """
    Immutable input to ExecutionEngine.
    """

    policy_result: PolicyResult
    market_state: MarketState

    capital_snapshot: CapitalSnapshot
    position_snapshot: PositionSnapshot

    current_price: float  # REQUIRED for price-based sizing

    engine_time: datetime  # REQUIRED

    stop_price: Optional[float] = None  # OPTIONAL (must come last)