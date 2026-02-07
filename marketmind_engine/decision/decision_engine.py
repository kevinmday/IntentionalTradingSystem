"""
Decision Engine

Evaluates a MarketState against registered decision rules
and produces a transparent, explainable DecisionResult.

This engine is intentionally deterministic and ML-free.
"""

from typing import List

from marketmind_engine.decision.state import MarketState
from marketmind_engine.decision.types import RuleResult, DecisionResult
from marketmind_engine.decision.eligibility import evaluate_eligibility
from marketmind_engine.decision.confirmation import confirm_market_capacity

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
    Canonical DecisionEngine (Phase 5B–5C)

    - Executes deterministic decision rules
    - Evaluates eligibility (observation only)
    - Evaluates market capacity (observation only)
    - Aggregates RuleResults
    - Emits ALLOW_BUY only when intent is present
      and no structural or participation blocks exist

    NOTE:
    Eligibility and market confirmation do NOT gate decisions yet.
    They are recorded for transparency and replay analysis.
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
        # Phase-5B / 5C: Observational gates
        # --------------------------------------------------

        eligibility = evaluate_eligibility(state)
        market_confirmation = confirm_market_capacity(state)

        # --------------------------------------------------
        # Phase 1 decision logic (unchanged, intent-only)
        # --------------------------------------------------

        intent_triggered = any(
            r.name == "NarrativeAcceleration" and r.triggered
            for r in rule_results
        )

        blocked_rules = [
            r.name
            for r in rule_results
            if r.triggered and r.name != "NarrativeAcceleration"
        ]

        decision = (
            "ALLOW_BUY"
            if intent_triggered and not blocked_rules
            else "NO_ACTION"
        )

        return DecisionResult(
            decision=decision,
            triggered_rules=[r.name for r in rule_results if r.triggered],
            blocked_rules=blocked_rules,
            metadata={
                # Phase-5B
                "eligible": eligibility.eligible,
                "eligibility_reason": eligibility.reason,
                # Phase-5C
                "market_confirmed": market_confirmation.confirmed,
                "market_confirmation_reason": market_confirmation.reason,
            },
        )