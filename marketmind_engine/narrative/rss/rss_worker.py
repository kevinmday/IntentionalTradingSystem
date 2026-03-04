import time
from marketmind_engine.narrative.feed_aggregator import FeedAggregator


class RSSWorker:
    """
    Background polling worker.
    Still no threading.
    Now normalizes entries through FeedAggregator.
    """

    def __init__(self, registry, fetcher, buffer):
        self.registry = registry
        self.fetcher = fetcher
        self.buffer = buffer
        self.aggregator = FeedAggregator()

    def poll_once(self):
        raw_entries = {}

        for url in self.registry.get_feeds():
            entries = self.fetcher.fetch(url)
            raw_entries[url] = entries

        normalized_items = self.aggregator.aggregate(raw_entries)

        self.buffer.update(normalized_items)

    def run_loop(self, interval_seconds=60):
        while True:
            self.poll_once()
            time.sleep(interval_seconds)
