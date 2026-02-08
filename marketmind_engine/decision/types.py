"""
Decision engine types (Phase-6E).
"""

from dataclasses import dataclass
from typing import List

from marketmind_engine.decision.rules.base import RuleResult


@dataclass(frozen=True)
class DecisionResult:
    """
    Aggregate decision output from the engine.

    Phase-6E:
    - decision is a simple string (ALLOW_BUY / NO_ACTION)
    - rule_results contains the full, explainable rule trace
    """

    decision: str
    rule_results: List[RuleResult]