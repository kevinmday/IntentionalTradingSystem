"""
Decision Engine

Evaluates a MarketState against registered decision rules
and produces a transparent, explainable DecisionResult.

This engine is intentionally deterministic and ML-free.
"""

from typing import List

from marketmind_engine.decision.state import MarketState
from marketmind_engine.decision.types import RuleResult, DecisionResult
from marketmind_engine.decision.rules.narrative_acceleration import (
    NarrativeAccelerationRule,
)


class DecisionEngine:
    """
    Canonical DecisionEngine (Phase 1)

    - Executes deterministic decision rules
    - Aggregates RuleResults
    - Emits ALLOW_BUY when justified
    - Leaves risk, sizing, and execution to later layers
    """

    def __init__(self):
        # Explicit rule registration (no magic)
        self.rules = [
            NarrativeAccelerationRule(),
        ]

    def evaluate(self, state: MarketState) -> DecisionResult:
        """
        Evaluate all registered rules against the given MarketState.
        """

        rule_results: List[RuleResult] = []

        for rule in self.rules:
            result = rule.evaluate(state)
            if result is not None:
                rule_results.append(result)

        # --------------------------------------------------
        # Phase 1 decision logic (simple, explicit)
        # --------------------------------------------------
        allow_buy = any(
            r.triggered and r.recommendation == "ALLOW_BUY"
            for r in rule_results
        )

        decision = "ALLOW_BUY" if allow_buy else "NO_ACTION"

        return DecisionResult(
            decision=decision,
            rule_results=rule_results,
            metadata={
                "engine": "DecisionEngine",
                "rule_count": len(self.rules),
                "allow_buy": allow_buy,
            },
        )
