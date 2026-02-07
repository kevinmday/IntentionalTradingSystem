"""
UCIP — Unified Cosmic Intention Postulate

This module defines the canonical UCIP equation used by MarketMind.
It is a pure mathematical transform with no side effects.
"""

from typing import Union


Number = Union[int, float]


def compute_ucip(
    intention: Number,
    scale: Number,
    ff_factor: Number = 1.0,
) -> float:
   def compute_ucip(
    intention: Number,
    scale: Number,
    ff_factor: Number = 1.0,
) -> float:
    """
    Compute UCIP (Unified Cosmic Intention Postulate).

    UCIP = Intention + Scale + Fundamental Force Factor

    Parameters
    ----------
    intention : int | float
        Directional intention signal (e.g. -1, 0, +1 or normalized value)
    scale : int | float
        Magnitude or scope of influence
    ff_factor : int | float, optional
        Fundamental force modifier (default = 1.0)

    Returns
    -------
    float
        Raw UCIP value (unrounded)
    """
    return float(intention) + float(scale) + float(ff_factor)
