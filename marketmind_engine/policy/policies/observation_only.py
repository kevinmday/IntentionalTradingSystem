from marketmind_engine.policy.policy_base import BasePolicy, PolicyInput
from marketmind_engine.policy.policy_result import PolicyResult
from marketmind_engine.policy.policy_types import PolicyAction


class ObservationOnlyPolicy(BasePolicy):
    """
    Baseline policy.

    Observes decisions without permitting action.
    Used to validate end-to-end policy plumbing.
    """

    @property
    def name(self) -> str:
        return "ObservationOnlyPolicy"

    def evaluate(self, input: PolicyInput) -> PolicyResult:
        triggered = [
            r.rule_name
            for r in input.decision_result.rule_results
            if r.triggered
        ]

        return PolicyResult(
            action=PolicyAction.HOLD,
            confidence=1.0,
            triggered_rules=triggered,
            gating_reasons=[
                "Observation-only mode: no actions permitted"
            ],
            policy_name=self.name,
        )
