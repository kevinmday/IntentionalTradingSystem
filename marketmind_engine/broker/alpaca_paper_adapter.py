from datetime import datetime, UTC
import os

from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce

from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import (
    StockLatestQuoteRequest,
    StockLatestTradeRequest,
    StockBarsRequest,
    StockSnapshotRequest,
)
from alpaca.data.timeframe import TimeFrame

from .broker_adapter import BrokerAdapter
from marketmind_engine.execution.execution_types import OrderIntent
from marketmind_engine.execution.execution_receipt import ExecutionReceipt


class AlpacaPaperBrokerAdapter(BrokerAdapter):
    """
    Live Alpaca Paper Trading Adapter.

    Provides:
        • Order execution
        • Live market data
        • Batch data for propagation engine
        • Percent change vs previous close
    """

    def __init__(self):

        api_key = os.getenv("APCA_API_KEY_ID")
        secret_key = os.getenv("APCA_API_SECRET_KEY")

        if not api_key or not secret_key:
            raise RuntimeError("Alpaca API keys not found in environment.")

        self.client = TradingClient(api_key, secret_key, paper=True)
        self.data_client = StockHistoricalDataClient(api_key, secret_key)

    # --------------------------------------------------
    # Identity
    # --------------------------------------------------

    @property
    def name(self) -> str:
        return "alpaca"

    # --------------------------------------------------
    # MARKET DATA
    # --------------------------------------------------

    def get_price(self, symbol: str):

        try:

            trade_req = StockLatestTradeRequest(symbol_or_symbols=symbol)
            trade = self.data_client.get_stock_latest_trade(trade_req)[symbol]

            if trade and trade.price:
                return float(trade.price)

        except Exception:
            pass

        try:

            req = StockLatestQuoteRequest(symbol_or_symbols=symbol)
            quote = self.data_client.get_stock_latest_quote(req)[symbol]

            bid = quote.bid_price
            ask = quote.ask_price

            if bid and ask:
                return float((bid + ask) / 2)

        except Exception:
            pass

        return None

    def get_prices(self, symbols):

        prices = {}

        for s in symbols:

            try:
                prices[s] = self.get_price(s)
            except Exception:
                prices[s] = None

        return prices

    # --------------------------------------------------
    # PREVIOUS CLOSE
    # --------------------------------------------------

    def _get_previous_close(self, symbol):

        prev_close = None

        # Attempt daily bars first
        try:

            bars_request = StockBarsRequest(
                symbol_or_symbols=symbol,
                timeframe=TimeFrame.Day,
                limit=2
            )

            bars = self.data_client.get_stock_bars(bars_request)

            bar_list = bars.data.get(symbol)

            if bar_list and len(bar_list) >= 2:
                prev_close = bar_list[-2].close

        except Exception:
            pass

        # Snapshot fallback (CORRECT FIELD)
        if prev_close is None:

            try:

                snap_req = StockSnapshotRequest(symbol_or_symbols=symbol)
                snap = self.data_client.get_stock_snapshot(snap_req)

                prev_close = snap[symbol].previous_daily_bar.close

            except Exception:
                pass

        return prev_close

    # --------------------------------------------------
    # API COMPATIBILITY
    # --------------------------------------------------

    def get_batch_data(self, symbols, context=None):

        prices = self.get_prices(symbols)

        results = {}

        for symbol in symbols:

            price = prices.get(symbol)
            prev_close = self._get_previous_close(symbol)

            if price and prev_close:

                pct = ((price - prev_close) / prev_close) * 100

                results[symbol] = {
                    "price": price,
                    "percent_change": round(pct, 4)
                }

            else:

                results[symbol] = {
                    "price": price,
                    "percent_change": None
                }

        return results

    def get_symbol_data(self, symbol: str, context=None):

        try:

            price = self.get_price(symbol)
            prev_close = self._get_previous_close(symbol)

            if price and prev_close:

                pct = ((price - prev_close) / prev_close) * 100

                return {
                    "price": price,
                    "percent_change": round(pct, 4),
                }

            return {
                "price": price,
                "percent_change": None,
            }

        except Exception:

            return {
                "price": None,
                "percent_change": None,
            }

    # --------------------------------------------------
    # EXECUTION
    # --------------------------------------------------

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