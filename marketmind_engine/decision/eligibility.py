"""
Eligibility rules (Phase-5B).

Determines whether an asset is eligible for consideration
based on intention, coherence, and chaos.

No execution. No price. No capital.
"""

from dataclasses import dataclass
from marketmind_engine.decision.state import MarketState


@dataclass(frozen=True)
class EligibilityResult:
    eligible: bool
    reason: str


# --------------------------------------------------
# Eligibility thresholds (policy, not math)
# --------------------------------------------------

FILS_MIN = 0.20     # minimum intention strength
UCIP_MIN = 0.30     # coherence floor
TTCF_MAX = 0.60     # chaos ceiling


def evaluate_eligibility(state: MarketState) -> EligibilityResult:
    """
    Evaluate whether a MarketState is eligible for consideration.

    This function is OBSERVATIONAL ONLY in Phase-5B.
    """

    if state.fils is None or state.fils < FILS_MIN:
        return EligibilityResult(
            eligible=False,
            reason="FILS below minimum",
        )

    if state.ucip is None or state.ucip < UCIP_MIN:
        return EligibilityResult(
            eligible=False,
            reason="UCIP below coherence floor",
        )

    if state.ttcf is not None and state.ttcf > TTCF_MAX:
        return EligibilityResult(
            eligible=False,
            reason="TTCF exceeds chaos ceiling",
        )

    return EligibilityResult(
        eligible=True,
        reason="Eligible by intention/coherence/chaos",
    )