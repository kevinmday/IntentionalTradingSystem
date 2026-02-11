from datetime import datetime, UTC
import uuid

from .broker_adapter import BrokerAdapter
from marketmind_engine.execution.execution_types import OrderIntent
from marketmind_engine.execution.execution_receipt import ExecutionReceipt


class PaperBrokerAdapter(BrokerAdapter):
    """
    Deterministic local paper broker.

    No network.
    Always accepts orders.
    """

    @property
    def name(self) -> str:
        return "PaperBroker"

    def submit(self, order_intent: OrderIntent) -> ExecutionReceipt:

        return ExecutionReceipt(
            broker_name=self.name,
            symbol=order_intent.symbol,
            side=order_intent.side,
            quantity=order_intent.quantity,
            order_type=order_intent.order_type,
            broker_order_id=str(uuid.uuid4()),
            accepted=True,
            message="Paper execution accepted",
            timestamp_utc=datetime.now(UTC),
        )
