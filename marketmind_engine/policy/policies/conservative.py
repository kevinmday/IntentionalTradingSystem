from marketmind_engine.policy.policy_base import BasePolicy, PolicyInput
from marketmind_engine.policy.policy_result import PolicyResult
from marketmind_engine.policy.policy_types import PolicyAction


class ConservativePolicy(BasePolicy):
    """
    Conservative policy.

    Requires corroboration across rules before allowing action.
    Defaults to WATCH or BLOCK under uncertainty.
    """

    @property
    def name(self) -> str:
        return "ConservativePolicy"

    def evaluate(self, input: PolicyInput) -> PolicyResult:
        triggered_rules = [
            r.rule_name
            for r in input.decision_result.rule_results
            if r.triggered
        ]

        trigger_count = len(triggered_rules)

        # --------------------------------------------------
        # No rule confidence → HOLD
        # --------------------------------------------------
        if trigger_count == 0:
            return PolicyResult(
                action=PolicyAction.HOLD,
                confidence=0.95,
                triggered_rules=[],
                gating_reasons=[
                    "No decision rules triggered"
                ],
                policy_name=self.name,
            )

        # --------------------------------------------------
        # Single rule → WATCH (insufficient corroboration)
        # --------------------------------------------------
        if trigger_count == 1:
            return PolicyResult(
                action=PolicyAction.WATCH,
                confidence=0.70,
                triggered_rules=triggered_rules,
                gating_reasons=[
                    "Single rule trigger; corroboration required"
                ],
                policy_name=self.name,
            )

        # --------------------------------------------------
        # Multiple rules → ALLOW (still non-executing)
        # --------------------------------------------------
        return PolicyResult(
            action=PolicyAction.ALLOW,
            confidence=min(0.85 + 0.05 * (trigger_count - 2), 0.95),
            triggered_rules=triggered_rules,
            gating_reasons=[
                "Multiple independent rule confirmations"
            ],
            policy_name=self.name,
        )
