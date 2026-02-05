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
from marketmind_engine.decision.rules.volatility_compression import (
    VolatilityCompressionRule,
)
from marketmind_engine.decision.rules.liquidity_participation import (
    LiquidityParticipationRule,
)


class DecisionEngine:
    """
    Canonical DecisionEngine (Phase 1)

    - Executes deterministic decision rules
    - Aggregates RuleResults
    - Emits ALLOW_BUY only when intent is present
      and no structural or participation blocks exist
    """

    def __init__(self):
        # Explicit rule registration (order matters)
        self.rules = [
            NarrativeAccelerationRule(),      # Rule 1: Intent
            VolatilityCompressionRule(),      # Rule 2: Structure
            LiquidityParticipationRule(),     # Rule 3: Participation
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
        # Phase 1 decision logic (explicit, deterministic)
        # --------------------------------------------------

        intent_triggered = any(
            r.rule_name == "NarrativeAcceleration" and r.triggered
            for r in rule_results
        )

        blocked = any(
            r.rule_name in (
                "VolatilityCompression",
                "LiquidityParticipation",
            ) and r.triggered
            for r in rule_results
        )

        allow_buy = intent_triggered and not blocked

        decision = "ALLOW_BUY" if allow_buy else "NO_ACTION"

        return DecisionResult(
            decision=decision,
            rule_results=rule_results,
            metadata={
                "engine": "DecisionEngine",
                "rule_count": len(self.rules),
                "intent_triggered": intent_triggered,
                "blocked": blocked,
            },
        )