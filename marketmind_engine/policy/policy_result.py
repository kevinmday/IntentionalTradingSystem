from dataclasses import dataclass
from typing import List
from .policy_types import PolicyAction


@dataclass(frozen=True)
class PolicyResult:
    """
    Output of the PolicyEngine.

    Must be explainable, replayable, and deterministic.
    """

    action: PolicyAction
    confidence: float  # Range: 0.0 – 1.0
    triggered_rules: List[str]
    gating_reasons: List[str]
    policy_name: str
