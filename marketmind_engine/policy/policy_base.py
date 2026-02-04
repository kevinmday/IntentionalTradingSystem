from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime

from marketmind_engine.decision.results import DecisionResult
from marketmind_engine.market_state import MarketState


@dataclass(frozen=True)
class PolicyInput:
    """
    Immutable input to all policies.
    """

    decision_result: DecisionResult
    market_state: MarketState
    engine_time: datetime


class BasePolicy(ABC):
    """
    Policies interpret rule outcomes.

    They do NOT:
    - fetch data
    - compute indicators
    - mutate state
    - execute trades
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """
        Human-readable policy identifier.
        """
        pass

    @abstractmethod
    def evaluate(self, input: PolicyInput):
        """
        Evaluate a decision result under this policy.

        Must return a PolicyResult.
        Must be deterministic.
        """
        pass
