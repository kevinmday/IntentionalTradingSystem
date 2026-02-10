"""
Domain Sensitivities — MarketMind Theory Layer

Defines how each market domain weights personality components.

Sensitivities control *how strongly* personality traits influence
allocation bias and exit shaping within a domain.

They do NOT:
- change direction
- override domain envelopes
- trigger entries or exits

This module is THEORY-ONLY.
"""

from typing import Dict


# -----------------------------
# Domain Sensitivity Weights
# -----------------------------
# Each weight lies in [0, 1].
#
# Higher value → domain is MORE sensitive to that personality trait
# Lower value  → domain is LESS sensitive to that trait
#
# Keys:
#   D — decay responsiveness
#   O — overshoot tendency
#   E — exit hostility
#   R — intent reliability
# -----------------------------

DOMAIN_SENSITIVITIES: Dict[str, Dict[str, float]] = {
    # Broad, liquid equities
    "equities": {
        "D": 0.4,
        "O": 0.3,
        "E": 0.3,
        "R": 0.6,
    },

    # High-reflexivity, narrative-driven AI / tech
    "ai": {
        "D": 0.8,
        "O": 0.9,
        "E": 0.6,
        "R": 0.8,
    },

    # Macro / rates / FX-like behavior
    "macro": {
        "D": 0.2,
        "O": 0.2,
        "E": 0.2,
        "R": 0.4,
    },

    # Illiquid / speculative / small-cap
    "speculative": {
        "D": 0.9,
        "O": 0.9,
        "E": 0.9,
        "R": 0.3,
    },
}


# -----------------------------
# Validation (Fail Fast)
# -----------------------------

def _validate_sensitivities() -> None:
    required_keys = {"D", "O", "E", "R"}

    for domain, weights in DOMAIN_SENSITIVITIES.items():
        if set(weights.keys()) != required_keys:
            raise ValueError(
                f"Domain '{domain}' sensitivities must define exactly {required_keys}, "
                f"got {set(weights.keys())}"
            )

        for k, v in weights.items():
            if not 0.0 <= v <= 1.0:
                raise ValueError(
                    f"Sensitivity {domain}.{k} must be in [0,1], got {v}"
                )


_validate_sensitivities()


# -----------------------------
# Public Accessor
# -----------------------------

def get_domain_sensitivities(domain: str) -> Dict[str, float]:
    """
    Return the sensitivity weights for a given domain.

    Raises KeyError if domain is unknown.
    """
    key = domain.lower()
    if key not in DOMAIN_SENSITIVITIES:
        raise KeyError(f"Unknown domain '{domain}' — no sensitivities defined")
    return DOMAIN_SENSITIVITIES[key].copy()