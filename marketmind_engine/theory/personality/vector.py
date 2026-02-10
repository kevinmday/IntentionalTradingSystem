"""
Personality Vector — MarketMind Theory Layer

Defines the minimal, sufficient personality representation for an asset.

This module is THEORY-ONLY:
- No data access
- No execution logic
- No time awareness

Personality shapes *how* allocation and exits behave,
but never predicts direction or triggers trades.
"""

from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class PersonalityVector:
    """
    Minimal personality vector for an asset.

    All components are normalized to [0.0, 1.0].

    D — Decay responsiveness
        How quickly narrative intent stops working.

    O — Overshoot tendency
        Propensity for sharp spikes vs smooth continuation.

    E — Exit hostility
        Liquidity / slippage pain when exiting.

    R — Intent reliability
        How often narrative meaning actually matters for this asset.
    """

    D: float
    O: float
    E: float
    R: float

    def __post_init__(self) -> None:
        for name, value in self.as_tuple(named=True):
            if not 0.0 <= value <= 1.0:
                raise ValueError(
                    f"Personality component {name}={value} is out of bounds [0,1]"
                )

    def as_tuple(self, *, named: bool = False) -> Tuple:
        """
        Return personality as a tuple.

        If named=True, returns ((name, value), ...)
        Otherwise returns (D, O, E, R)
        """
        if named:
            return (
                ("D", self.D),
                ("O", self.O),
                ("E", self.E),
                ("R", self.R),
            )
        return (self.D, self.O, self.E, self.R)

    @property
    def decay_tolerance(self) -> float:
        """
        Inverse of decay responsiveness.
        Higher means the asset tolerates weakening intent longer.
        """
        return 1.0 - self.D

    @property
    def overshoot_risk(self) -> float:
        """Direct expression of spike / snapback risk."""
        return self.O

    @property
    def exit_pressure(self) -> float:
        """
        Direct expression of exit hostility.
        Higher means tighter, faster exits are required.
        """
        return self.E

    @property
    def narrative_trust(self) -> float:
        """Degree to which narrative signals should be trusted."""
        return self.R


# Canonical neutral personality (safe default)
NEUTRAL_PERSONALITY = PersonalityVector(
    D=0.5,
    O=0.5,
    E=0.5,
    R=0.5,
)