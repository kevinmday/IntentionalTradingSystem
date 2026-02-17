import os
import requests
from datetime import datetime

class TradierAdapter:
    """
    Tradier Sandbox/Production execution adapter.
    Lives in Flask integration layer.
    """

    def __init__(self):
        self.token = os.getenv("TRADIER_API_KEY")
        self.base_url = os.getenv("TRADIER_BASE_URL")

        if not self.token:
            raise RuntimeError("TRADIER_API_KEY not set in environment")

        if not self.base_url:
            raise RuntimeError("TRADIER_BASE_URL not set in environment")

        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/json"
        }

    def place_market_order(self, account_id, symbol, side, quantity):
        url = f"{self.base_url}/accounts/{account_id}/orders"

        payload = {
            "class": "equity",
            "symbol": symbol,
            "side": side,
            "quantity": quantity,
            "type": "market",
            "duration": "day"
        }

        response = requests.post(url, headers=self.headers, data=payload)

        return {
            "status_code": response.status_code,
            "response": response.json(),
            "timestamp": datetime.utcnow().isoformat()
        }