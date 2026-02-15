from typing import Optional

from marketmind_engine.policy.policy_types import PolicyAction
from marketmind_engine.execution.policy.base import ExecutionDirective

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
    Stop-aware (optional).

    Phase 12.1:
    - Regime ExecutionDirective enforcement
    """

    DEFAULT_ORDER_TYPE = "market"

    def evaluate(
        self,
        input: ExecutionInput,
        execution_directive: Optional[ExecutionDirective] = None,
    ) -> Optional[OrderIntent]:

        policy = input.policy_result
        state = input.market_state
        capital = input.capital_snapshot
        positions = input.position_snapshot
        price = input.current_price
        stop = input.stop_price

        # --------------------------------------------------
        # REGIME ENTRY BLOCK (Phase 12.1)
        # --------------------------------------------------

        if execution_directive is not None:
            if not execution_directive.allow_entries:
                return None

        # --------------------------------------------------
        # Policy Authority Gate
        # --------------------------------------------------

        if policy.action != PolicyAction.ALLOW:
            return None

        # --------------------------------------------------
        # Duplicate Symbol Guard
        # --------------------------------------------------

        if state.symbol in positions.positions:
            return None

        # --------------------------------------------------
        # Price Validation
        # --------------------------------------------------

        if price is None or price <= 0:
            return None

        # --------------------------------------------------
        # Capital Risk Base
        # --------------------------------------------------

        risk_capital = capital.account_equity * capital.max_risk_per_trade

        if risk_capital <= 0:
            return None

        # --------------------------------------------------
        # Apply Regime Size Multiplier (Phase 12.1)
        # --------------------------------------------------

        if execution_directive is not None:
            risk_capital *= execution_directive.size_multiplier

            if risk_capital <= 0:
                return None

        # --------------------------------------------------
        # Stop-Based Risk Sizing (Preferred)
        # --------------------------------------------------

        if stop is not None:
            risk_per_share = price - stop

            if risk_per_share <= 0:
                return None

            quantity = risk_capital / risk_per_share
            rationale = "Intent approved with stop-based risk model"

        else:
            # --------------------------------------------------
            # Fallback: Price-Based Sizing
            # --------------------------------------------------

            position_value = min(risk_capital, capital.buying_power)

            if position_value <= 0:
                return None

            quantity = position_value / price
            rationale = "Intent approved with capital + price-based risk model"

        if quantity <= 0:
            return None

        return OrderIntent(
            symbol=state.symbol,
            side="buy",
            order_type=self.DEFAULT_ORDER_TYPE,
            quantity=round(quantity, 6),
            rationale=rationale,
            confidence=policy.confidence,
        )