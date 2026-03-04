"""
Synthetic Momentum Policy
Deterministic Replay Injection Layer

Purpose:
    Provide deterministic policy permission during replay
    before full RSS + DecisionEngine wiring is complete.

Rules:
    - No mutation of core logic
    - No synthetic alpha modeling
    - Only structural signal activation
    - Conform strictly to PolicyAction enum
"""

from marketmind_engine.policy.policy_types import PolicyAction


class SyntheticMomentumPolicy:
    """
    Minimal deterministic replay policy.

    Behavior:
        - If price_delta != 0 → ALLOW
        - Otherwise → HOLD

    NOTE:
        Policy expresses posture only.
        Directional execution is determined downstream.
    """

    def evaluate(self, market_state):

        delta = getattr(market_state, "price_delta", 0.0)

        if delta != 0:
            action = PolicyAction.ALLOW
            reason = "Synthetic momentum permission"
            confidence = 0.75
        else:
            action = PolicyAction.HOLD
            reason = "Synthetic neutral"
            confidence = 0.10

        return type("PolicyResult", (), {
            "action": action,
            "confidence": confidence,
            "reason": reason,
        })()
