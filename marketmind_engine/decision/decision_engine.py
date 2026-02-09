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
from marketmind_engine.decision.rules.bell_drake_threshold import (
    BellDrakeThreshold,
)


class DecisionEngine:
    """
    Canonical DecisionEngine (Phase-8B)

    - Executes deterministic rules via RuleRegistry
    - Aggregates RuleResults
    - Emits ALLOW_BUY ONLY when Bell-Drake triggers
    - No eligibility, capacity, or capital logic
    """

    def __init__(self):
        self.rule_registry = RuleRegistry(
            rules=[
                NarrativeAccelerationRule(),
                BellDrakeThreshold(),
            ]
        )

    def evaluate(self, state: MarketState) -> DecisionResult:
        """
        Evaluate all registered rules against the given MarketState.
        """

        rule_results = self.rule_registry.evaluate(state)

        decision = "NO_ACTION"

        # --------------------------------------------------
        # Phase-8B: Bell-Drake is intent authority
        # --------------------------------------------------
        for r in rule_results:
            if r.rule_name == "BellDrakeThreshold" and r.triggered:
                decision = "ALLOW_BUY"
                break

        return DecisionResult(
            decision=decision,
            rule_results=rule_results,
        )