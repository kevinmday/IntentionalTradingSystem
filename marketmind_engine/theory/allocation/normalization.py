"""
Allocation Normalization — MarketMind Theory Layer

Defines normalization logic for relative allocation weights.

This module:
- conserves total capital
- enforces non-negativity
- handles degenerate cases safely

This module is THEORY-ONLY:
- No prices
- No execution
- No accounts
"""

from typing import Dict


# -----------------------------
# Normalization Logic
# -----------------------------

def normalize_weights(weights: Dict[str, float]) -> Dict[str, float]:
    """
    Normalize a dictionary of non-negative weights so they sum to 1.0.

    Parameters
    ----------
    weights : Dict[str, float]
        Mapping from asset identifier to raw allocation weight.

    Returns
    -------
    Dict[str, float]
        Normalized weights summing to 1.0.

    Notes
    -----
    - Negative values are rejected.
    - If total weight is zero, returns zero-weight allocation.
    """

    for key, value in weights.items():
        if value < 0.0:
            raise ValueError(
                f"Allocation weight for '{key}' must be non-negative, got {value}"
            )

    total = sum(weights.values())

    if total == 0.0:
        # Degenerate case: no allocatable signal
        return {key: 0.0 for key in weights}

    return {key: value / total for key, value in weights.items()}


# -----------------------------
# Convenience Helper
# -----------------------------

def scale_to_capital(
    normalized_weights: Dict[str, float],
    total_capital: float,
) -> Dict[str, float]:
    """
    Scale normalized weights to absolute capital amounts.

    This helper is still THEORY-SAFE:
    it performs arithmetic only and does not place orders.

    Parameters
    ----------
    normalized_weights : Dict[str, float]
        Weights summing to 1.0.
    total_capital : float
        Total capital to distribute.

    Returns
    -------
    Dict[str, float]
        Capital allocation per asset.
    """

    if total_capital < 0.0:
        raise ValueError("total_capital must be non-negative")

    return {
        key: weight * total_capital
        for key, weight in normalized_weights.items()
    }