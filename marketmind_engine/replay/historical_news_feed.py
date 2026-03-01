@'
class HistoricalNewsFeed:
    """
    Deterministic historical news feed.

    events = [
        {"timestamp": int, "symbol": str, "sentiment": float, "headline": str}
    ]
    """

    def __init__(self, events: list):
        self._events = sorted(events, key=lambda e: e["timestamp"])
        self._cursor = 0

    def get_events_up_to(self, engine_time: int):
        released = []

        while self._cursor < len(self._events):
            event = self._events[self._cursor]

            if event["timestamp"] <= engine_time:
                released.append(event)
                self._cursor += 1
            else:
                break

        return released
'@ | Set-Content marketmind_engine\replay\historical_news_feed.py