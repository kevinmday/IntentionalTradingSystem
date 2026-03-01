"""
Synthetic Momentum Policy
Deterministic Replay Injection Layer

Purpose:
    Provide deterministic policy decisions during replay
    before full RSS + DecisionEngine wiring is complete.

Rules:
    - No mutation of core logic
    - No synthetic alpha modeling
    - Only structural signal activation
"""

from marketmind_engine.policy.policy_types import PolicyAction


class SyntheticMomentumPolicy:
    """
    Minimal deterministic replay policy.

    Behavior:
        - If price_delta > 0 → ALLOW_BUY
        - If price_delta < 0 → ALLOW_SELL
        - Otherwise → HOLD
    """

    def evaluate(self, market_state):

        delta = getattr(market_state, "price_delta", 0.0)

        if delta > 0:
            action = PolicyAction.ALLOW_BUY
            reason = "Synthetic upward momentum"
            confidence = 0.75

        elif delta < 0:
            action = PolicyAction.ALLOW_SELL
            reason = "Synthetic downward momentum"
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