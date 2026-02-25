import os
import requests


class AlpacaPaperAdapter:
    """
    Minimal Alpaca Paper Trading Adapter.
    Phase: Close The Loop.

    Submits market buy orders only.
    """

    def __init__(self):
        self.base_url = "https://paper-api.alpaca.markets"
        self.api_key = os.getenv("APCA_API_KEY_ID")
        self.secret_key = os.getenv("APCA_API_SECRET_KEY")

        if not self.api_key or not self.secret_key:
            raise RuntimeError("Alpaca API credentials not set in environment variables.")

        self.headers = {
            "APCA-API-KEY-ID": self.api_key,
            "APCA-API-SECRET-KEY": self.secret_key,
            "Content-Type": "application/json",
        }

    def submit_market_buy(self, symbol: str, qty: int = 1):
        url = f"{self.base_url}/v2/orders"

        order_payload = {
            "symbol": symbol,
            "qty": qty,
            "side": "buy",
            "type": "market",
            "time_in_force": "day",
        }

        response = requests.post(url, json=order_payload, headers=self.headers)

        if response.status_code != 200:
            raise RuntimeError(f"Order failed: {response.text}")

        return response.json()