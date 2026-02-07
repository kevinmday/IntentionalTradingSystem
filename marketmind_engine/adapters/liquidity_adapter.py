from typing import Optional, Sequence
import statistics
from datetime import datetime, time
import pytz

from marketmind_engine.adapters.contracts import LiquidityContext
from marketmind_engine.observers.ignition import (
    IgnitionObserver,
    NullIgnitionObserver,
    IgnitionObservation,
)
from marketmind_engine.utils.market_time import seconds_from_open


ET = pytz.timezone("US/Eastern")


def is_market_open_window(now: datetime) -> bool:
    """
    Hard gate for open-window ignition relaxation.
    Policy-only gate; does not control order timing.
    """
    et = now.astimezone(ET)
    return time(9, 30) <= et.time() <= time(9, 40)


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

    # ---- Phase-3 Step-1 constants (non-binding ignition) ----
    IGNITION_RECENT_BARS = 3
    IGNITION_MIN_DELTA = 1.30

    RELAXATION_PROXIMITY = 0.90  # 90% of baseline threshold

    OPEN_RELAX_VOLUME_RATIO = 1.10
    OPEN_RELAX_TRADE_RATIO = 1.05
    # --------------------------------------------------------

    def __init__(
        self,
        window_size: int = 20,
        min_volume_ratio: float = 1.25,
        min_trade_ratio: float = 1.15,
        observer: Optional[IgnitionObserver] = None,
    ):
        self.window_size = window_size
        self.min_volume_ratio = min_volume_ratio
        self.min_trade_ratio = min_trade_ratio
        self.observer = observer or NullIgnitionObserver()

    def evaluate(
        self,
        *,
        volume_series: Sequence[float],
        trade_count_series: Optional[Sequence[int]] = None,
        now: Optional[datetime] = None,   # backward compatible
        symbol: Optional[str] = None,     # optional for harness
    ) -> Optional[LiquidityContext]:
        try:
            # -----------------------------
            # Baseline validation
            # -----------------------------
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

            # -----------------------------
            # Phase-3 Step-1: ignition delta
            # -----------------------------
            ignition_delta = None
            ignition_used = False

            if (
                now is not None
                and is_market_open_window(now)
                and len(volume_series) >= (self.IGNITION_RECENT_BARS + 1)
            ):
                recent_vols = volume_series[
                    -(self.IGNITION_RECENT_BARS + 1):-1
                ]
                last_vol = volume_series[-1]

                if trade_count_series is not None:
                    recent_trds = trade_count_series[
                        -(self.IGNITION_RECENT_BARS + 1):-1
                    ]
                    last_trd = trade_count_series[-1]
                else:
                    recent_trds = None
                    last_trd = None

                if recent_vols and statistics.mean(recent_vols) > 0:
                    vol_delta = last_vol / statistics.mean(recent_vols)
                else:
                    vol_delta = None

                if (
                    recent_trds is not None
                    and recent_trds
                    and statistics.mean(recent_trds) > 0
                ):
                    trd_delta = last_trd / statistics.mean(recent_trds)
                else:
                    trd_delta = None

                if vol_delta is not None and trd_delta is not None:
                    ignition_delta = min(vol_delta, trd_delta)

            # -----------------------------
            # Baseline participation check
            # -----------------------------
            baseline_volume_ok = volume_ratio >= self.min_volume_ratio
            baseline_trade_ok = trade_ok

            # -----------------------------
            # Soft relaxation (AND-only)
            # -----------------------------
            near_volume = False
            near_trade = False

            if (
                ignition_delta is not None
                and ignition_delta >= self.IGNITION_MIN_DELTA
            ):
                near_volume = volume_ratio >= (
                    self.min_volume_ratio * self.RELAXATION_PROXIMITY
                )
                near_trade = (
                    trade_ratio is None
                    or trade_ratio >= (
                        self.min_trade_ratio * self.RELAXATION_PROXIMITY
                    )
                )

                if near_volume and near_trade:
                    if (
                        volume_ratio >= self.OPEN_RELAX_VOLUME_RATIO
                        and (
                            trade_ratio is None
                            or trade_ratio >= self.OPEN_RELAX_TRADE_RATIO
                        )
                    ):
                        baseline_volume_ok = True
                        baseline_trade_ok = True
                        ignition_used = True

            participating = baseline_volume_ok and baseline_trade_ok

            # -----------------------------
            # Ignition Observation Harness
            # -----------------------------
            if now is not None:
                try:
                    obs = IgnitionObservation(
                        timestamp=now,
                        symbol=symbol or "UNKNOWN",
                        is_open_window=is_market_open_window(now),
                        seconds_from_open=seconds_from_open(now),

                        volume_ratio=volume_ratio,
                        trade_ratio=trade_ratio,
                        volume_median=volume_median,
                        trade_median=trade_median,

                        ignition_delta=ignition_delta,
                        ignition_used=ignition_used,

                        near_volume=near_volume,
                        near_trade=near_trade,

                        volume_threshold=self.min_volume_ratio,
                        trade_threshold=self.min_trade_ratio,
                        relax_volume_threshold=self.OPEN_RELAX_VOLUME_RATIO,
                        relax_trade_threshold=self.OPEN_RELAX_TRADE_RATIO,
                    )
                    self.observer.record(obs)
                except Exception:
                    pass  # observation must never affect execution

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
                    "ignition_delta": ignition_delta,
                    "ignition_used": ignition_used,
                },
            )

        except Exception:
            # Abstention > guessing
            return None