from .rss.feed_registry import FeedRegistry
from .rss.rss_fetcher import RSSFetcher
from .rss.narrative_buffer import NarrativeBuffer
from .rss.rss_worker import RSSWorker


class NarrativeAdapter:
    """
    Deterministic narrative shock adapter.

    Engine-safe:
    - No background threads required
    - No network calls required
    - Replay-safe
    - Fully injectable for testing

    Shock model:
    - 0.0 = no activity
    - 0.5 = moderate burst
    - 1.0 = extreme headline intensity
    """

    def __init__(self):
        self.registry = FeedRegistry()
        self.fetcher = RSSFetcher()
        self.buffer = NarrativeBuffer()
        self.worker = RSSWorker(self.registry, self.fetcher, self.buffer)

    # -------------------------------------------------
    # Deterministic Injection (Replay / Testing Mode)
    # -------------------------------------------------

    def inject_headlines(self, headlines):
        """
        Deterministically inject headlines into buffer.

        Used for:
        - Regime testing
        - Replay mode
        - Unit tests
        """
        if headlines is None:
            headlines = []

        self.buffer.update(list(headlines))

    # -------------------------------------------------
    # Shock Calculation
    # -------------------------------------------------

    def compute_narrative_shock(self) -> float:
        """
        Compute normalized headline shock.

        Current model:
        shock = headline_count / 100
        capped at 1.0

        This keeps the signal bounded and stable.
        """

        headlines = self.buffer.snapshot()

        if not headlines:
            return 0.0

        volume = len(headlines)

        shock = volume / 100.0

        return min(shock, 1.0)
