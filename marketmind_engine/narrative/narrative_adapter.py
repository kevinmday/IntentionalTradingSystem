from .rss.feed_registry import FeedRegistry
from .rss.rss_fetcher import RSSFetcher
from .rss.narrative_buffer import NarrativeBuffer
from .rss.rss_worker import RSSWorker

from marketmind_engine.narrative.projection.symbol_extractor import (
    SymbolExtractor,
)
from marketmind_engine.narrative.projection.projection_event import (
    ProjectionEvent,
)


class NarrativeAdapter:
    """
    Deterministic narrative shock adapter.

    Engine-safe.
    Projection contract locked.
    """

    def __init__(self):
        self.registry = FeedRegistry()
        self.fetcher = RSSFetcher()
        self.buffer = NarrativeBuffer()
        self.worker = RSSWorker(self.registry, self.fetcher, self.buffer)

        self.extractor = SymbolExtractor()

        self._projection_events = []
        self._engine_time_counter = 0  # deterministic local counter

    # -------------------------------------------------
    # Deterministic Injection
    # -------------------------------------------------

    def inject_headlines(self, headlines):

        if headlines is None:
            headlines = []

        self.buffer.update(list(headlines))
        self._update_projection()

    # -------------------------------------------------
    # Projection (STRUCTURED CONTRACT)
    # -------------------------------------------------

    def _extract_title(self, item):
        """
        Support both legacy dict items and NarrativeItem objects.
        """

        if isinstance(item, dict):
            return item.get("title", "")

        # NarrativeItem object
        return getattr(item, "title", "")

    def _update_projection(self):

        headlines = self.buffer.snapshot()

        events = []
        symbols = set()

        for item in headlines:

            title = self._extract_title(item)

            extracted = self.extractor.extract(title)

            for symbol in extracted:
                symbols.add(symbol)

        # Deterministic event creation
        for symbol in sorted(symbols):

            self._engine_time_counter += 1

            events.append(
                ProjectionEvent(
                    symbol=symbol,
                    engine_time=self._engine_time_counter,
                    source="rss",
                    sentiment=0.0,  # v1 neutral
                    weight=1.0,     # v1 unit weight
                )
            )

        self._projection_events = events

    def get_projection_events(self):
        return list(self._projection_events)

    # -------------------------------------------------
    # Shock Calculation
    # -------------------------------------------------

    def compute_narrative_shock(self) -> float:

        headlines = self.buffer.snapshot()

        if not headlines:
            return 0.0

        volume = len(headlines)
        shock = volume / 100.0

        return min(shock, 1.0)