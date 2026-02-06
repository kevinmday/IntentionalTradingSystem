from typing import Optional, Sequence
import statistics

from marketmind_engine.adapters.contracts import LiquidityContext


class LiquidityAdapter:
    """
    Detects whether market participation is real and sufficient.

    Owns:
    - windowing
    - normalization
    - thresholds

    Returns:
    - LiquidityContext or None

    Fails silently by design.
    """

    def __init__(
        self,
        window_size: int = 20,
        min_volume_ratio: float = 1.25,
        min_trade_ratio: float = 1.15,
    ):
        self.window_size = window_size
        self.min_volume_ratio = min_volume_ratio
        self.min_trade_ratio = min_trade_ratio

    def evaluate(
        self,
        *,
        volume_series: Sequence[float],
        trade_count_series: Optional[Sequence[int]] = None,
    ) -> Optional[LiquidityContext]:
        try:
            if not volume_series or len(volume_series) < self.window_size:
                return None

            recent_volumes = volume_series[-self.window_size:]
            current_volume = recent_volumes[-1]

            volume_median = statistics.median(recent_volumes)
            if volume_median <= 0:
                return None

            volume_ratio = current_volume / volume_median

            trade_ratio = None
            trade_ok = True

            if trade_count_series is not None:
                if len(trade_count_series) < self.window_size:
                    return None

                recent_trades = trade_count_series[-self.window_size:]
                trade_median = statistics.median(recent_trades)
                if trade_median <= 0:
                    return None

                trade_ratio = recent_trades[-1] / trade_median
                trade_ok = trade_ratio >= self.min_trade_ratio

            participating = (
                volume_ratio >= self.min_volume_ratio
                and trade_ok
            )

            return LiquidityContext(
                participating=participating,
                window=f"{self.window_size}p",
                metric="volume_trade_ratio",
                metadata={
                    "current_volume": current_volume,
                    "volume_median": volume_median,
                    "volume_ratio": volume_ratio,
                    "trade_ratio": trade_ratio,
                    "volume_threshold": self.min_volume_ratio,
                    "trade_threshold": self.min_trade_ratio,
                },
            )

        except Exception:
            # Abstention > guessing
            return None