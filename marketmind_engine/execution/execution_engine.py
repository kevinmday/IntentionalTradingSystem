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
    Capital-aware.
    Price-aware.
    """

    DEFAULT_ORDER_TYPE = "market"

    def evaluate(self, input: ExecutionInput) -> Optional[OrderIntent]:

        policy = input.policy_result
        state = input.market_state
        capital = input.capital_snapshot
        positions = input.position_snapshot
        price = input.current_price

        # Only ALLOW produces an order intent
        if policy.action != PolicyAction.ALLOW:
            return None

        # Duplicate symbol guard
        if state.symbol in positions.positions:
            return None

        # Price validation
        if price is None or price <= 0:
            return None

        # ---- Capital-Aware Risk Sizing ----
        risk_capital = capital.account_equity * capital.max_risk_per_trade
        position_value = min(risk_capital, capital.buying_power)

        if position_value <= 0:
            return None

        # ---- Price-Based Quantity ----
        quantity = position_value / price

        if quantity <= 0:
            return None

        return OrderIntent(
            symbol=state.symbol,
            side="buy",
            order_type=self.DEFAULT_ORDER_TYPE,
            quantity=round(quantity, 6),
            rationale="Intent approved with capital + price-based risk model",
            confidence=policy.confidence,
        )