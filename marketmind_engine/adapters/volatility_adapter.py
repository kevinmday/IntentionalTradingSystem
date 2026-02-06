from typing import Optional, Sequence
import statistics

from marketmind_engine.adapters.contracts import VolatilityContext


class VolatilityAdapter:
    """
    Detects volatility compression relative to recent regime.

    This adapter:
    - owns windowing, normalization, and thresholds
    - returns VolatilityContext or None
    - fails silently
    """

    def __init__(
        self,
        window_size: int = 20,
        compression_percentile: float = 0.25,
    ):
        self.window_size = window_size
        self.compression_percentile = compression_percentile

    def evaluate(
        self,
        atr_series: Sequence[float],
    ) -> Optional[VolatilityContext]:
        """
        atr_series: rolling ATR or realized volatility values
        """
        try:
            if atr_series is None:
                return None

            if len(atr_series) < self.window_size:
                return None

            recent = atr_series[-self.window_size:]
            current = recent[-1]

            if current <= 0:
                return None

            sorted_vals = sorted(recent)
            cutoff_index = int(len(sorted_vals) * self.compression_percentile)
            cutoff_value = sorted_vals[cutoff_index]

            compressed = current <= cutoff_value

            return VolatilityContext(
                compressed=compressed,
                window=f"{self.window_size}d",
                metric="atr_percentile",
                metadata={
                    "current_atr": current,
                    "percentile_cutoff": cutoff_value,
                    "percentile": self.compression_percentile,
                },
            )

        except Exception:
            # Fail silently by contract
            return None