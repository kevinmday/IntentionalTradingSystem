"""
Decision Engine Scaffold

Evaluates a MarketState against registered rules
and produces a transparent decision report.
"""

from typing import Callable, List

from marketmind_engine.decision.state import MarketState
from marketmind_engine.decision.types import RuleResult, DecisionResult


# A rule is a callable that takes MarketState and returns RuleResult
Rule = Callable[[MarketState], RuleResult]


class DecisionEngine:
    """
    Minimal decision engine.

    - Holds a list of rules
    - Evaluates them against a state
    - Reports what fired
    """

    def __init__(self, rules: List[Rule]):
        self.rules = rules

    def evaluate(self, state: MarketState) -> DecisionResult:
        """
        Evaluate all rules against the given state.
        """

        triggered = []
        blocked = []

        for rule in self.rules:
            result = rule(state)

            if result.triggered:
                triggered.append(result.name)
            else:
                blocked.append(result.name)

        # NOTE: Decision is intentionally dumb for now
        decision = "UNDECIDED"

        return DecisionResult(
            decision=decision,
            triggered_rules=triggered,
            blocked_rules=blocked,
        )
