"""
TTCF — Chaos / Entropy Metric

This module defines the TTCF (Trump Tensor Chaos Factor),
a normalized measure of instability within intention signals.

TTCF is intentionally agnostic to data source (NLP, indicators,
simulation). It operates only on numeric inputs.
"""

from typing import Union


Number = Union[int, float]


def compute_ttcf(
    sentiment: Number,
    intention_weight: Number,
) -> float:
    """
    Compute TTCF (chaos factor).

    Parameters
    ----------
    sentiment : int | float
        Signed sentiment score (expected range ~[-1, 1])
    intention_weight : int | float
        Aggregate intention magnitude (non-negative)

    Returns
    -------
    float
        Chaos factor in range [0.0, 1.0]
    """

    # Base chaos rises with absolute sentiment magnitude
    sentiment_chaos = abs(float(sentiment)) * 0.4

    # Additional instability from uneven intention weight
    weight_chaos = (float(intention_weight) % 2.0) * 0.1

    ttcf = sentiment_chaos + weight_chaos

    # Clamp to [0, 1]
    return max(0.0, min(ttcf, 1.0))
