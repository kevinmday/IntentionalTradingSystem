"""
Lock-In Shape — MarketMind Theory Layer

Defines lock-in behavior parameters derived from exit shape.

Lock-in is a PROFIT PROTECTION MECHANISM, not an exit trigger.
Quant-owned systems decide *when* to engage lock-in.
This module defines *how* lock-in behaves once engaged.

This module is THEORY-ONLY:
- No prices
- No execution
- No P/L tracking
- No time awareness
"""

from dataclasses import dataclass

from .exit_shape import ExitShape


# -----------------------------
# Lock-In Control Vector
# -----------------------------

@dataclass(frozen=True)
class LockInShape:
    """
    Lock-in behavior control parameters.

    All values are normalized to [0.0, 1.0].

    Interpretation:
    - activation_bias      → how eagerly lock-in should be enabled
    - protected_fraction  → portion of gains to protect once active
    - release_leniency    → how easily lock-in relaxes if conditions improve
    """

    activation_bias: float
    protected_fraction: float
    release_leniency: float


# -----------------------------
# Exit Shape → Lock-In Mapping
# -----------------------------

def lockin_shape_from_exit(exit_shape: ExitShape) -> LockInShape:
    """
    Derive lock-in behavior from exit shape.

    Mapping doctrine:
    - Higher lock-in urgency → earlier activation
    - Higher exit pressure  → larger protected fraction
    - Higher decay tolerance → more lenient release
    """

    activation_bias = exit_shape.lockin_urgency

    protected_fraction = min(
        1.0,
        0.5 + exit_shape.exit_pressure * 0.4
    )

    release_leniency = exit_shape.decay_tolerance

    return LockInShape(
        activation_bias=activation_bias,
        protected_fraction=protected_fraction,
        release_leniency=release_leniency,
    )