from typing import Iterable, Mapping, Any, Optional
from datetime import datetime, timedelta

from marketmind_engine.adapters.contracts import NarrativeContext


class NarrativeAdapter:
    """
    Interprets raw narrative events and determines whether
    narrative acceleration is present.

    This adapter is opinionated.
    The decision kernel is not.
    """

    def __init__(
        self,
        lookback_hours: int = 6,
        min_sources: int = 2,
        acceleration_ratio: float = 1.5,
    ):
        self.lookback_hours = lookback_hours
        self.min_sources = min_sources
        self.acceleration_ratio = acceleration_ratio

    def build(
        self,
        raw_events: Optional[Iterable[Mapping[str, Any]]]
    ) -> Optional[NarrativeContext]:
        """
        raw_events expected shape (minimal):
        [
          {
            "source": "Reuters",
            "timestamp": datetime | ISO8601 string
          },
          ...
        ]
        """

        if not raw_events:
            return None

        now = datetime.utcnow()
        window_start = now - timedelta(hours=self.lookback_hours)

        recent_events = []
        for e in raw_events:
            ts = self._parse_time(e.get("timestamp"))
            if ts and ts >= window_start:
                recent_events.append(e)

        if len(recent_events) < self.min_sources:
            return None

        midpoint = now - timedelta(hours=self.lookback_hours / 2)

        early = 0
        late = 0
        sources = set()

        for e in recent_events:
            ts = self._parse_time(e.get("timestamp"))
            if not ts:
                continue

            sources.add(e.get("source"))

            if ts < midpoint:
                early += 1
            else:
                late += 1

        if early == 0:
            accelerating = late >= self.min_sources
        else:
            accelerating = (late / early) >= self.acceleration_ratio

        if not accelerating:
            return None

        return NarrativeContext(
            accelerating=True,
            source_count=len(sources),
            window=f"{self.lookback_hours}h",
            notes=f"{early} → {late} event acceleration",
            mentions_prior=early,
            mentions_previous=early,
            mentions_current=late,
        )

    @staticmethod
    def _parse_time(value) -> Optional[datetime]:
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            try:
                return datetime.fromisoformat(value)
            except ValueError:
                return None
        return None