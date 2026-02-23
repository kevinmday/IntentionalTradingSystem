from __future__ import annotations

from typing import Optional

from marketmind_engine.decision.types import DecisionResult
from marketmind_engine.execution.execution_types import OrderIntent
from marketmind_engine.execution.execution_receipt import ExecutionReceipt
from marketmind_engine.broker.broker_adapter import BrokerAdapter


class ExecutionService:
    """
    Engine-level execution bridge.

    Pure transport orchestrator.
    No scoring.
    No risk logic.
    No lifecycle management.
    """

    def __init__(self, broker: BrokerAdapter):
        self._broker = broker

    # --------------------------------------------------
    # Path 1 — Decision-driven execution (unit test path)
    # --------------------------------------------------

    def execute(
        self,
        decision: DecisionResult,
        symbol: str,
        quantity: float,
        rationale: str,
        confidence: float,
    ) -> Optional[ExecutionReceipt]:

        if decision.decision not in ("ALLOW_BUY", "ALLOW_SELL"):
            return None

        side = "buy" if decision.decision == "ALLOW_BUY" else "sell"

        order_intent = OrderIntent(
            symbol=symbol,
            side=side,
            order_type="market",
            quantity=quantity,
            rationale=rationale,
            confidence=confidence,
        )

        return self._broker.submit(order_intent)

    # --------------------------------------------------
    # Path 2 — Direct OrderIntent submission (runtime path)
    # --------------------------------------------------

    def submit_intent(
        self,
        order_intent: OrderIntent,
    ) -> ExecutionReceipt:
        """
        Submit a fully constructed OrderIntent.
        Used by RuntimeExecutor after TradeCoordinator.
        """

        return self._broker.submit(order_intent)