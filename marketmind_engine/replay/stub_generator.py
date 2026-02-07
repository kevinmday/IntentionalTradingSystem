from datetime import datetime, timedelta
from typing import Iterable, List
import pytz

from marketmind_engine.data.bars import MarketBar


UTC = pytz.UTC


def _utc(ts: datetime) -> datetime:
    if ts.tzinfo is None:
        return ts.replace(tzinfo=UTC)
    return ts.astimezone(UTC)


def generate_flat_open(
    *,
    start_time: datetime,
    bars: int = 10,
    volume: float = 100.0,
    trades: int = 10,
    bar_minutes: int = 1,
) -> List[MarketBar]:
    """
    Flat, non-participating open.
    Expect: NO_ACTION, no ignition.
    """
    start = _utc(start_time)
    series: List[MarketBar] = []

    for i in range(bars):
        ts = start + timedelta(minutes=bar_minutes * (i + 1))
        series.append(
            MarketBar(
                timestamp=ts,
                volume=volume,
                trade_count=trades,
            )
        )

    return series


def generate_rising_participation(
    *,
    start_time: datetime,
    bars: int = 15,
    base_volume: float = 100.0,
    base_trades: int = 10,
    volume_step: float = 20.0,
    trade_step: int = 2,
    bar_minutes: int = 1,
) -> List[MarketBar]:
    """
    Gradual participation increase.
    Expect: still conservative, maybe near thresholds.
    """
    start = _utc(start_time)
    series: List[MarketBar] = []

    vol = base_volume
    trd = base_trades

    for i in range(bars):
        ts = start + timedelta(minutes=bar_minutes * (i + 1))
        series.append(
            MarketBar(
                timestamp=ts,
                volume=vol,
                trade_count=trd,
            )
        )
        vol += volume_step
        trd += trade_step

    return series


def generate_ignition_spike(
    *,
    start_time: datetime,
    bars: int = 12,
    base_volume: float = 100.0,
    base_trades: int = 10,
    spike_multiplier: float = 2.0,
    bar_minutes: int = 1,
) -> List[MarketBar]:
    """
    Sudden ignition-like spike after quiet bars.
    Expect: ignition_delta present, maybe near thresholds.
    """
    start = _utc(start_time)
    series: List[MarketBar] = []

    # quiet bars
    for i in range(bars - 1):
        ts = start + timedelta(minutes=bar_minutes * (i + 1))
        series.append(
            MarketBar(
                timestamp=ts,
                volume=base_volume,
                trade_count=base_trades,
            )
        )

    # spike bar
    spike_ts = start + timedelta(minutes=bar_minutes * bars)
    series.append(
        MarketBar(
            timestamp=spike_ts,
            volume=base_volume * spike_multiplier,
            trade_count=int(base_trades * spike_multiplier),
        )
    )

    return series


def chain(*segments: Iterable[MarketBar]) -> List[MarketBar]:
    """
    Utility to concatenate multiple stub segments.
    """
    out: List[MarketBar] = []
    for seg in segments:
        out.extend(seg)
    return out