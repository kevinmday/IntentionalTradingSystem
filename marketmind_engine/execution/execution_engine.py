from typing import Optional

from marketmind_engine.policy.policy_types import PolicyAction

from .execution_input import ExecutionInput
from .execution_types import OrderIntent


class ExecutionEngine:
    """
    Translates PolicyResult into OrderIntent.

    Deterministic.
    Stateless.
    Broker-agnostic.
    """

    DEFAULT_ORDER_TYPE = "market"
    DEFAULT_QUANTITY = 1.0  # Stub until capital logic added

    def evaluate(self, input: ExecutionInput) -> Optional[OrderIntent]:

        policy = input.policy_result
        state = input.market_state

        # Only ALLOW produces an order intent
        if policy.action != PolicyAction.ALLOW:
            return None

        return OrderIntent(
            symbol=state.symbol,
            side="buy",
            order_type=self.DEFAULT_ORDER_TYPE,
            quantity=self.DEFAULT_QUANTITY,
            rationale="Intent approved by policy",
            confidence=policy.confidence,
        )
