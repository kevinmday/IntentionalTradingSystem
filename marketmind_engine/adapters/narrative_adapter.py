from typing import Iterable, Mapping, Any, Optional
from datetime import datetime, timedelta, timezone

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

        # Timezone-aware UTC (no deprecated utcnow usage)
        now = datetime.now(timezone.utc)
        window_start = now - timedelta(hours=self.lookback_hours)

        recent_events = []
        for event in raw_events:
            ts = self._parse_time(event.get("timestamp"))
            if ts and ts >= window_start:
                recent_events.append(event)

        if len(recent_events) < self.min_sources:
            return None

        midpoint = now - timedelta(hours=self.lookback_hours / 2)

        early = 0
        late = 0
        sources = set()

        for event in recent_events:
            ts = self._parse_time(event.get("timestamp"))
            if not ts:
                continue

            source = event.get("source")
            if source:
                sources.add(source)

            if ts < midpoint:
                early += 1
            else:
                late += 1

        # Acceleration logic
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
        """
        Accepts:
        - datetime (naive or aware)
        - ISO8601 string
        Returns:
        - timezone-aware UTC datetime
        """

        if isinstance(value, datetime):
            if value.tzinfo is None:
                return value.replace(tzinfo=timezone.utc)
            return value.astimezone(timezone.utc)

        if isinstance(value, str):
            try:
                dt = datetime.fromisoformat(value)
                if dt.tzinfo is None:
                    return dt.replace(tzinfo=timezone.utc)
                return dt.astimezone(timezone.utc)
            except ValueError:
                return None

        return None