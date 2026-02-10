"""
Allocation Core — MarketMind Theory Layer

Defines the canonical allocation weighting function:

    f(domain, personality)

This function produces a *relative allocation weight* based on:
- hard domain envelopes
- domain-specific personality sensitivities
- asset personality vector

It does NOT:
- allocate dollars
- know account balances
- place orders
- observe prices

This module is THEORY-ONLY.
"""

from typing import Dict

from ..domains.envelopes import get_domain_envelope
from ..domains.sensitivities import get_domain_sensitivities
from ..personality.vector import PersonalityVector


# -----------------------------
# Allocation Bias Components
# -----------------------------

def _bias_from_personality(
    personality: PersonalityVector,
    sensitivities: Dict[str, float],
) -> float:
    """
    Compute multiplicative bias from personality and domain sensitivities.

    Bias is constructed so that:
    - Higher decay responsiveness (D) reduces weight
    - Higher overshoot tendency (O) reduces weight
    - Higher exit hostility (E) reduces weight
    - Higher intent reliability (R) increases weight
    """

    D, O, E, R = personality.as_tuple()

    wD = sensitivities["D"]
    wO = sensitivities["O"]
    wE = sensitivities["E"]
    wR = sensitivities["R"]

    b_D = 1.0 - wD * D
    b_O = 1.0 - wO * O
    b_E = 1.0 - wE * E
    b_R = 1.0 + wR * (R - 0.5)

    bias = b_D * b_O * b_E * b_R

    # Guard against pathological collapse
    return max(bias, 0.0)


# -----------------------------
# Public Allocation Function
# -----------------------------

def allocation_weight(domain: str, personality: PersonalityVector) -> float:
    """
    Compute the relative allocation weight for an asset.

    Returns a non-negative scalar suitable for normalization
    across a basket of assets.

    This function enforces:
    - hard domain envelope
    - personality-weighted bias
    """

    envelope = get_domain_envelope(domain)
    sensitivities = get_domain_sensitivities(domain)

    bias = _bias_from_personality(personality, sensitivities)

    weight = envelope * bias

    # Hard non-negativity
    return max(weight, 0.0)