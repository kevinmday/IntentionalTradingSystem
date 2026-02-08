from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Candidate:
    symbol: str
    domain: str

    # Intention state
    fils: float
    ucip: float
    ttcf: float

    # Evaluations
    eligible: bool
    eligibility_reason: str

    market_confirmed: bool
    market_confirmation_reason: str

    # Decision engine
    decision: str

    # Provenance
    engine_time: str