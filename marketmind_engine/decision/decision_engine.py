"""
Decision Engine

Evaluates a MarketState against registered decision rules
and produces a transparent, explainable DecisionResult.

This engine is intentionally deterministic and ML-free.
"""

from marketmind_engine.decision.state import MarketState
from marketmind_engine.decision.types import DecisionResult

from marketmind_engine.decision.rules.registry import RuleRegistry
from marketmind_engine.decision.rules.intent.narrative_acceleration import (
    NarrativeAccelerationRule,
)


class DecisionEngine:
    """
    Canonical DecisionEngine (Phase-6E)

    - Executes deterministic rules via RuleRegistry
    - Aggregates RuleResults
    - Emits ALLOW_BUY only when intent rules trigger
    - No eligibility, capacity, or capital logic
    """

    def __init__(self):
        self.rule_registry = RuleRegistry(
            rules=[
                NarrativeAccelerationRule(),
            ]
        )

    def evaluate(self, state: MarketState) -> DecisionResult:
        """
        Evaluate all registered rules against the given MarketState.
        """

        rule_results = self.rule_registry.evaluate(state)

        # --------------------------------------------------
        # Phase-6E decision logic (intent-only stub)
        # --------------------------------------------------

        decision = "NO_ACTION"
        if any(r.triggered for r in rule_results):
            decision = "ALLOW_BUY"

        return DecisionResult(
            decision=decision,
            rule_results=rule_results,
        )