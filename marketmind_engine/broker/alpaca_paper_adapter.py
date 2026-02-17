from datetime import datetime, UTC
import os

from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce

from .broker_adapter import BrokerAdapter
from marketmind_engine.execution.execution_types import OrderIntent
from marketmind_engine.execution.execution_receipt import ExecutionReceipt


class AlpacaPaperBrokerAdapter(BrokerAdapter):
    """
    Live Alpaca Paper Trading Adapter.
    """

    def __init__(self):
        api_key = os.getenv("APCA_API_KEY_ID")
        secret_key = os.getenv("APCA_API_SECRET_KEY")

        if not api_key or not secret_key:
            raise RuntimeError("Alpaca API keys not found in environment.")

        self.client = TradingClient(api_key, secret_key, paper=True)

    @property
    def name(self) -> str:
        return "AlpacaPaper"

    def submit(self, order_intent: OrderIntent) -> ExecutionReceipt:

        side = OrderSide.BUY if order_intent.side.lower() == "buy" else OrderSide.SELL

        order_request = MarketOrderRequest(
            symbol=order_intent.symbol,
            qty=order_intent.quantity,
            side=side,
            time_in_force=TimeInForce.DAY,
        )

        try:
            order = self.client.submit_order(order_request)

            return ExecutionReceipt(
                broker_name=self.name,
                symbol=order.symbol,
                side=order.side.value,
                quantity=float(order.qty),
                order_type="market",
                broker_order_id=order.id,
                accepted=True,
                message="Submitted to Alpaca Paper",
                timestamp_utc=datetime.now(UTC),
            )

        except Exception as e:
            return ExecutionReceipt(
                broker_name=self.name,
                symbol=order_intent.symbol,
                side=order_intent.side,
                quantity=order_intent.quantity,
                order_type=order_intent.order_type,
                broker_order_id="N/A",
                accepted=False,
                message=str(e),
                timestamp_utc=datetime.now(UTC),
            )
