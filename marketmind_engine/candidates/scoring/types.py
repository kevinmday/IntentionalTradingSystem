# marketmind_engine/candidates/scoring/types.py

from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class ScoredCandidate:
    """
    Phase-6B scored candidate artifact.

    Immutable.
    Deterministic.
    Explainable.
    """

    # Identity (copied from Candidate)
    domain: str
    symbol: str
    decision: str
    eligible: bool
    market_ok: bool

    # Scoring outputs
    components: Dict[str, float]
    score: float
    priority: str
    explanation: str