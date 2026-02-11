from datetime import datetime
from typing import List

from .policy_base import BasePolicy, PolicyInput
from .policy_result import PolicyResult
from .policy_types import PolicyAction


class IntentExecutionPolicy(BasePolicy):
    """
    Minimal v1 policy.

    Translates DecisionEngine intent into
    permission posture.

    - ALLOW_BUY  → ALLOW
    - NO_ACTION  → HOLD

    No constraint enforcement.
    No capital logic.
    No protection overrides.
    """

    @property
    def name(self) -> str:
        return "IntentExecutionPolicy"

    def evaluate(self, input: PolicyInput) -> PolicyResult:
        decision = input.decision_result.decision

        if decision == "ALLOW_BUY":
            action = PolicyAction.ALLOW
            confidence = 1.0
            gating_reasons: List[str] = []
        else:
            action = PolicyAction.HOLD
            confidence = 0.5
            gating_reasons = ["No intent trigger"]

        triggered_rules = [
            r.rule_name
            for r in input.decision_result.rule_results
            if r.triggered
        ]

        return PolicyResult(
            action=action,
            confidence=confidence,
            triggered_rules=triggered_rules,
            gating_reasons=gating_reasons,
            policy_name=self.name,
        )