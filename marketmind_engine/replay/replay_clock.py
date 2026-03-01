class ReplayClock:
    """
    Deterministic replay clock.
    Advances in seconds.
    """

    def __init__(self, start_time: int = 0):
        self._time = start_time

    def now(self) -> int:
        return self._time

    def advance(self, seconds: int) -> None:
        self._time += seconds