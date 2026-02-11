from dataclasses import dataclass
from datetime import datetime

from marketmind_engine.policy.policy_result import PolicyResult
from marketmind_engine.decision.state import MarketState


@dataclass(frozen=True)
class ExecutionInput:
    """
    Immutable input to ExecutionEngine.
    """

    policy_result: PolicyResult
    market_state: MarketState
    engine_time: datetime
