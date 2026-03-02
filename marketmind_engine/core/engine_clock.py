class EngineClock:
    """
    Monotonic engine decision clock.

    This clock tracks engine cycle progression,
    NOT real-world time.

    It is deterministic and advances explicitly
    per engine execution cycle.
    """

    def __init__(self, start_time: int = 0):
        self._time = start_time

    def now(self) -> int:
        return self._time

    def advance(self, step: int = 1) -> None:
        if step < 0:
            raise ValueError("EngineClock cannot move backwards.")
        self._time += step