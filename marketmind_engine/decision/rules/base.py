from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional

from marketmind_engine.decision.state import MarketState


class RuleCategory(Enum):
    """
    Semantic category of a rule.
    Determines execution order and authority.
    """
    INTENT = "intent"
    CONSTRAINT = "constraint"
    HYBRID = "hybrid"
    PROTECTION = "protection"


@dataclass(frozen=True)
class RuleResult:
    """
    Immutable result of a rule evaluation.
    """
    rule_name: str
    category: RuleCategory

    triggered: bool
    score_delta: float = 0.0
    block: bool = False
    override: Optional[str] = None

    reason: str = ""


class BaseRule:
    """
    Base contract for all DecisionEngine rules.

    Rules MUST:
    - Be deterministic
    - Be stateless
    - Never mutate MarketState
    - Return a RuleResult
    """

    name: str = "BaseRule"
    category: RuleCategory | None = None

    def evaluate(self, state: MarketState) -> RuleResult:
        raise NotImplementedError("Rule must implement evaluate()")
