"""
Bell–Drake Threshold Rule

Detects whether cumulative micro-intention signals exceed
a critical threshold indicating macro-level emergence.
"""

from typing import Iterable


def bell_drake_threshold(
    values: Iterable[float],
    threshold: float = 1.0,
) -> bool:
    """
    Evaluate Bell–Drake threshold crossing.

    Parameters
    ----------
    values : Iterable[float]
        Collection of micro-intention values (e.g. FILS components,
        fractal cascade outputs, or weighted signals).
    threshold : float, optional
        Critical threshold for macro emergence (default = 1.0).

    Returns
    -------
    bool
        True if cumulative intention >= threshold, else False.
    """

    total = sum(values)
    return total >= threshold
