"""
Deterministic Synthetic Historical Price Feed
Replay Harness Implementation
"""

class HistoricalPriceFeed:
    """
    Deterministic price curve:

    Minutes 0–5: flat at 100
    Minutes 6–10: steady rise
    Minutes 11–15: spike
    Minutes 16–20: drop
    """

    def __init__(self, clock):
        self._clock = clock

    def get_price(self, symbol: str) -> float:
        """
        Engine expects get_price(symbol).
        We derive engine_time internally from injected clock.
        """

        engine_time = self._clock.now()
        minute = engine_time // 60

        if minute <= 5:
            return 100.0

        elif 6 <= minute <= 10:
            return 100.0 + (minute - 5)

        elif 11 <= minute <= 15:
            return 110.0

        elif 16 <= minute <= 20:
            return 110.0 - (minute - 15) * 3

        return 100.0
