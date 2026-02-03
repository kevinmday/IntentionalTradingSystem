"""
Decision engine types.
"""

from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class RuleResult:
    """
    Result returned by a decision rule.
    """
    name: str
    triggered: bool
    notes: str | None = None


@dataclass(frozen=True)
class DecisionResult:
    """
    Aggregate decision output from the engine.
    """
    decision: str
    triggered_rules: List[str]
    blocked_rules: List[str]
