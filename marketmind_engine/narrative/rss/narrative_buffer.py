import threading


class NarrativeBuffer:
    \"\"\"
    Thread-safe storage for latest headlines snapshot.
    \"\"\"

    def __init__(self):
        self._lock = threading.Lock()
        self._headlines = []

    def update(self, headlines):
        with self._lock:
            self._headlines = headlines

    def snapshot(self):
        with self._lock:
            return list(self._headlines)
