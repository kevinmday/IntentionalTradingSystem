"""
Exit Shape — MarketMind Theory Layer

Defines how exit behavior is shaped by asset personality.

This module maps personality traits into exit-control parameters
that QUANT-owned exit logic may consume once an exit is triggered.

This module:
- does NOT trigger exits
- does NOT observe prices
- does NOT manage P/L
- does NOT override quant authority

It answers only:
    \"How should exits behave for this asset?\"
"""

from dataclasses import dataclass

from ..personality.vector import PersonalityVector


# -----------------------------
# Exit Control Vector
# -----------------------------

@dataclass(frozen=True)
class ExitShape:
    """
    Exit behavior control parameters.

    All values are normalized to [0.0, 1.0].

    Higher values generally imply:
    - tighter
    - faster
    - more conservative exits
    """

    decay_tolerance: float
    lockin_urgency: float
    trail_aggressiveness: float
    exit_pressure: float


# -----------------------------
# Personality → Exit Mapping
# -----------------------------

def exit_shape_from_personality(personality: PersonalityVector) -> ExitShape:
    """
    Map personality traits into exit control parameters.

    Mapping doctrine:
    - High decay responsiveness → low decay tolerance
    - High overshoot tendency   → high lock-in urgency
    - High exit hostility      → high trail aggressiveness & pressure
    - High intent reliability  → modestly relaxed exits
    """

    D, O, E, R = personality.as_tuple()

    # Inverse decay responsiveness
    decay_tolerance = 1.0 - D

    # Overshoot risk demands faster profit protection
    lockin_urgency = O

    # Exit hostility tightens trailing behavior
    trail_aggressiveness = E

    # Narrative reliability slightly tempers exit pressure
    exit_pressure = min(1.0, E + (0.5 - R) * 0.3)

    return ExitShape(
        decay_tolerance=decay_tolerance,
        lockin_urgency=lockin_urgency,
        trail_aggressiveness=trail_aggressiveness,
        exit_pressure=exit_pressure,
    )