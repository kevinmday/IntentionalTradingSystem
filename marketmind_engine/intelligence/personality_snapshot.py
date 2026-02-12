from dataclasses import dataclass


@dataclass(frozen=True)
class PersonalitySnapshot:
    """
    Immutable advisory intelligence snapshot.

    This does NOT control authority.
    It only modulates confidence weighting.
    """

    symbol: str
    exit_reliability: float = 1.0  # neutral multiplier