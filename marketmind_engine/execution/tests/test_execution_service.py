from datetime import datetime, UTC

from marketmind_engine.execution.execution_service import ExecutionService
from marketmind_engine.execution.execution_receipt import ExecutionReceipt
from marketmind_engine.execution.execution_types import OrderIntent
from marketmind_engine.decision.types import DecisionResult
from marketmind_engine.broker.broker_adapter import BrokerAdapter


class FakeBrokerAdapter(BrokerAdapter):
    """
    Deterministic fake broker for unit testing.
    """

    @property
    def name(self) -> str:
        return "FakeBroker"

    def submit(self, order_intent: OrderIntent) -> ExecutionReceipt:
        return ExecutionReceipt(
            broker_name=self.name,
            symbol=order_intent.symbol,
            side=order_intent.side,
            quantity=order_intent.quantity,
            order_type=order_intent.order_type,
            broker_order_id="FAKE-123",
            accepted=True,
            message="Fake execution",
            timestamp_utc=datetime.now(UTC),
        )


def test_execution_service_allow_buy():

    broker = FakeBrokerAdapter()
    service = ExecutionService(broker)

    decision = DecisionResult(
        decision="ALLOW_BUY",
        rule_results=[],
    )

    receipt = service.execute(
        decision,
        symbol="AAPL",
        quantity=10,
        rationale="unit-test",
        confidence=0.99,
    )

    assert receipt is not None
    assert receipt.accepted is True
    assert receipt.symbol == "AAPL"
    assert receipt.quantity == 10
    assert receipt.broker_order_id == "FAKE-123"


def test_execution_service_no_action():

    broker = FakeBrokerAdapter()
    service = ExecutionService(broker)

    decision = DecisionResult(
        decision="NO_ACTION",
        rule_results=[],
    )

    receipt = service.execute(
        decision,
        symbol="AAPL",
        quantity=10,
        rationale="unit-test",
        confidence=0.99,
    )

    assert receipt is None
