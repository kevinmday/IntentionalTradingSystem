from .policy_base import BasePolicy, PolicyInput
from .policy_result import PolicyResult


class PolicyEngine:
    """
    Applies exactly one policy to a DecisionResult.

    No chaining, voting, or weighting in v1.
    """

    def __init__(self, policy: BasePolicy):
        self._policy = policy

    @property
    def policy_name(self) -> str:
        return self._policy.name

    def evaluate(self, input: PolicyInput) -> PolicyResult:
        return self._policy.evaluate(input)
