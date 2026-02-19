from typing import Dict, List


class SyntheticPriceFeed:
    """
    Deterministic time-indexed price feed.

    Example:
        {"AAPL": [100, 101, 102]}

    Index = clock.now()
    """

    def __init__(self, series: Dict[str, List[float]], clock):
        self._series = series
        self._clock = clock

    def price(self, symbol: str) -> float:
        ts = self._clock.now()

        if symbol not in self._series:
            raise KeyError(f"Symbol '{symbol}' not in synthetic feed.")

        if ts >= len(self._series[symbol]):
            raise IndexError(
                f"No price defined for symbol '{symbol}' at ts={ts}."
            )

        return self._series[symbol][ts]
