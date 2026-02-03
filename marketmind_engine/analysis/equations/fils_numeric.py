"""
FILS (Numeric Aggregation)

This module defines the legacy numeric form of the
Future Intention Likelihood Scale (FILS), computed
as a simple aggregation of micro-intention scores.

This is a pure, deterministic transform.
"""

from typing import Iterable


def compute_fils(scores: Iterable[float]) -> float:
    """
    Compute FILS as the arithmetic mean of micro-intention scores.

    Parameters
    ----------
    scores : Iterable[float]
        Collection of numeric intention signals. Expected to be
        normalized or semi-normalized upstream.

    Returns
    -------
    float
        Raw FILS value. Returns 0.0 if no scores are provided.
    """

    values = list(scores)

    if not values:
        return 0.0

    return sum(values) / len(values)
