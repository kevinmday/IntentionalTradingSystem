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
from marketmind_engine.decision.rules.constraint.narrative_price_latency import (
    NarrativePriceLatencyRule,
)


class DecisionEngine:
    """
    Canonical DecisionEngine (Phase-9C enhanced)

    - Executes deterministic rules via RuleRegistry
    - Aggregates RuleResults
    - Bell-Drake remains intent authority
    - Constraint rules may veto via block=True
    - No eligibility, capacity, or capital logic
    """

    def __init__(self):
        self.rule_registry = RuleRegistry(
            rules=[
                NarrativeAccelerationRule(),
                BellDrakeThreshold(),
                NarrativePriceLatencyRule(),  # Phase-9C constraint gate
            ]
        )

    def evaluate(self, state: MarketState) -> DecisionResult:
        """
        Evaluate all registered rules against the given MarketState.
        """

        rule_results = self.rule_registry.evaluate(state)

        decision = "NO_ACTION"

        bell_drake_triggered = False
        blocked = False

        # --------------------------------------------------
        # Evaluate rule authority + veto
        # --------------------------------------------------
        for r in rule_results:

            # Constraint veto
            if r.block:
                blocked = True

            # Intent authority
            if r.rule_name == "BellDrakeThreshold" and r.triggered:
                bell_drake_triggered = True

        # --------------------------------------------------
        # Final decision logic
        # --------------------------------------------------
        if bell_drake_triggered and not blocked:
            decision = "ALLOW_BUY"

        return DecisionResult(
            decision=decision,
            rule_results=rule_results,
        )