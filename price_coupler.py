import os
from dotenv import load_dotenv
from alpaca.trading.client import TradingClient
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import (
    StockLatestTradeRequest,
    StockBarsRequest
)
from alpaca.data.timeframe import TimeFrame
from datetime import datetime, timedelta


load_dotenv(override=True)


class PriceCoupler:
    """
    Session-aware price and volume metrics.

    Market OPEN:
        price_delta = displacement over recent intraday window
        volume_ratio = recent bar vs intraday average

    Market CLOSED:
        price_delta = displacement vs previous close
        volume_ratio = 1.0
    """

    def __init__(self):
        api_key = os.getenv("APCA_API_KEY_ID")
        api_secret = os.getenv("APCA_API_SECRET_KEY")

        self.trading_client = TradingClient(api_key, api_secret, paper=True)
        self.data_client = StockHistoricalDataClient(api_key, api_secret)

    def market_is_open(self) -> bool:
        clock = self.trading_client.get_clock()
        return clock.is_open

    def get_price_metrics(self, symbol: str):

        # --- Latest trade (IEX feed)
        trade_request = StockLatestTradeRequest(
            symbol_or_symbols=symbol,
            feed="iex"
        )

        latest_trade = self.data_client.get_stock_latest_trade(trade_request)
        current_price = latest_trade[symbol].price

        if self.market_is_open():
            return self._intraday_metrics(symbol, current_price)
        else:
            return self._closed_market_metrics(symbol, current_price)

    # -------------------------
    # OPEN MARKET LOGIC
    # -------------------------
    def _intraday_metrics(self, symbol: str, current_price: float):

        end = datetime.utcnow()
        start = end - timedelta(minutes=15)

        bars_request = StockBarsRequest(
            symbol_or_symbols=symbol,
            timeframe=TimeFrame.Minute,
            start=start,
            end=end,
            feed="iex"
        )

        bars = self.data_client.get_stock_bars(bars_request)

        if symbol not in bars or len(bars[symbol]) < 2:
            return {
                "price": float(current_price),
                "price_delta": 0.0,
                "volume_ratio": 1.0
            }

        first_bar = bars[symbol][0]
        last_bar = bars[symbol][-1]

        price_delta = (current_price - first_bar.close) / first_bar.close

        avg_volume = sum(bar.volume for bar in bars[symbol]) / len(bars[symbol])
        volume_ratio = last_bar.volume / avg_volume if avg_volume else 1.0

        return {
            "price": float(current_price),
            "price_delta": float(price_delta),
            "volume_ratio": float(volume_ratio)
        }

    # -------------------------
    # CLOSED MARKET LOGIC
    # -------------------------
    def _closed_market_metrics(self, symbol: str, current_price: float):

        end = datetime.utcnow()
        start = end - timedelta(days=5)

        bars_request = StockBarsRequest(
            symbol_or_symbols=symbol,
            timeframe=TimeFrame.Day,
            start=start,
            end=end,
            feed="iex"
        )

        bars = self.data_client.get_stock_bars(bars_request)

        if symbol not in bars or len(bars[symbol]) < 1:
            return {
                "price": float(current_price),
                "price_delta": 0.0,
                "volume_ratio": 1.0
            }

        previous_close = bars[symbol][-1].close
        price_delta = (current_price - previous_close) / previous_close

        return {
            "price": float(current_price),
            "price_delta": float(price_delta),
            "volume_ratio": 1.0
        }