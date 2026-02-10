"""
Domain Envelopes — MarketMind Theory Layer

Defines hard capital caps by market domain.

Domain envelopes represent structural market physics:
- liquidity depth
- reflexivity
- stability
- execution risk

These envelopes are NON-NEGOTIABLE caps.
No signal, personality, or optimizer may override them.

This module is THEORY-ONLY:
- No prices
- No execution
- No accounts
"""

from typing import Dict


# -----------------------------
# Domain Capital Envelopes
# -----------------------------
# Values represent MAXIMUM fraction of total deployable capital
# that may be allocated to a given domain.
#
# All values must lie in (0, 1].
# -----------------------------

DOMAIN_ENVELOPES: Dict[str, float] = {
    # Broad, liquid equities
    "equities": 0.60,

    # High-reflexivity, narrative-driven tech
    "ai": 0.35,

    # Macro / rates / FX-like exposures
    "macro": 0.50,

    # Illiquid / speculative / small-cap
    "speculative": 0.20,
}


# -----------------------------
# Validation (Fail Fast)
# -----------------------------

def _validate_envelopes() -> None:
    for domain, cap in DOMAIN_ENVELOPES.items():
        if not 0.0 < cap <= 1.0:
            raise ValueError(
                f"Domain envelope for '{domain}' must be in (0,1], got {cap}"
            )


_validate_envelopes()


# -----------------------------
# Public Accessor
# -----------------------------

def get_domain_envelope(domain: str) -> float:
    """
    Return the hard capital envelope for a given domain.

    Raises KeyError if domain is unknown.
    """
    key = domain.lower()
    if key not in DOMAIN_ENVELOPES:
        raise KeyError(f"Unknown domain '{domain}' — no envelope defined")
    return DOMAIN_ENVELOPES[key]