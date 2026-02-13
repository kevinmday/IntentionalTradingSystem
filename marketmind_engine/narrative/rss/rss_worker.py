import time


class RSSWorker:
    \"\"\"
    Background polling worker.
    Stub only — does not start thread yet.
    \"\"\"

    def __init__(self, registry, fetcher, buffer):
        self.registry = registry
        self.fetcher = fetcher
        self.buffer = buffer

    def poll_once(self):
        headlines = []

        for url in self.registry.get_feeds():
            headlines.extend(self.fetcher.fetch(url))

        self.buffer.update(headlines)

    def run_loop(self, interval_seconds=60):
        while True:
            self.poll_once()
            time.sleep(interval_seconds)
