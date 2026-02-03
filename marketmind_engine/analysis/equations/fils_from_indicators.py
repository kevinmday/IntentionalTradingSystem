"""
FILS from Indicators (Hybrid Equation)

This module defines a deterministic mapping from
quantitative indicators (RSI, MACD histogram, UCIP)
into an intention-space likelihood score.

No policy or decision logic is embedded here.
"""

from typing import Union


Number = Union[int, float]


def compute_fils_from_indicators(
    rsi: Number,
    macd_hist: Number,
    ucip: Number,
) -> float:
    """
    Compute FILS using real-time indicator metrics.

    Parameters
    ----------
    rsi : int | float
        Relative Strength Index, expected range [0, 100]
    macd_hist : int | float
        MACD histogram value (can be negative or positive)
    ucip : int | float
        Unified Cosmic Intention Postulate value

    Returns
    -------
    float
        Raw FILS score in intention space (0–100 scale).
        Caller is responsible for rounding if needed.
    """

    # Normalize RSI → [0, 1]
    rsi_score = max(0.0, min(float(rsi) / 100.0, 1.0))

    # Normalize MACD histogram → [-1, 1]
    # Soft-scaled to avoid domination by outliers
    macd_score = max(-1.0, min(float(macd_hist) * 5.0, 1.0))

    # Normalize UCIP → [0, 1]
    # Assumes typical UCIP operating range ~[0, 5]
    ucip_score = max(0.0, min(float(ucip) / 5.0, 1.0))

    # Aggregate into raw FILS likelihood
    raw = (rsi_score + macd_score + ucip_score) / 3.0

    # Project into 0–100 FILS scale
    return raw * 100.0
