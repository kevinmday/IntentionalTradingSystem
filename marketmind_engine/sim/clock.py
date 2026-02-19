class DeterministicClock:
    """
    Explicitly controlled simulation clock.

    No dependency on system time.
    """

    def __init__(self, start_ts: int = 0):
        self._ts = start_ts

    def now(self) -> int:
        return self._ts

    def advance(self, delta: int = 1) -> None:
        if delta < 0:
            raise ValueError("Clock cannot move backward.")
        self._ts += delta
