from typing import List

from .policy_base import BasePolicy, PolicyInput
from .policy_result import PolicyResult
from .policy_types import PolicyAction


class LiquidityConstraintPolicy(BasePolicy):
    """
    Minimal constraint policy.

    If liquidity is below threshold,
    BLOCK even if intent is ALLOW_BUY.

    Otherwise mirror intent posture.
    """

    LIQUIDITY_THRESHOLD = 0.2

    @property
    def name(self) -> str:
        return "LiquidityConstraintPolicy"

    def evaluate(self, input: PolicyInput) -> PolicyResult:
        decision = input.decision_result.decision
        liquidity = input.market_state.liquidity or 0.0

        triggered_rules = [
            r.rule_name
            for r in input.decision_result.rule_results
            if r.triggered
        ]

        # ---- Constraint Authority ----
        if liquidity < self.LIQUIDITY_THRESHOLD:
            return PolicyResult(
                action=PolicyAction.BLOCK,
                confidence=1.0,
                triggered_rules=triggered_rules,
                gating_reasons=[f"Liquidity {liquidity:.2f} < {self.LIQUIDITY_THRESHOLD}"],
                policy_name=self.name,
            )

        # ---- Mirror Intent ----
        if decision == "ALLOW_BUY":
            return PolicyResult(
                action=PolicyAction.ALLOW,
                confidence=1.0,
                triggered_rules=triggered_rules,
                gating_reasons=[],
                policy_name=self.name,
            )

        return PolicyResult(
            action=PolicyAction.HOLD,
            confidence=0.5,
            triggered_rules=triggered_rules,
            gating_reasons=["No intent trigger"],
            policy_name=self.name,
        )