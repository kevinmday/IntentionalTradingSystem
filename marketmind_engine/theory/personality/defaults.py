"""
Personality Defaults — MarketMind Theory Layer

Defines canonical, domain-level default personality profiles.

These defaults are used when:
- an asset has no learned personality yet
- historical data is insufficient
- a safe, neutral prior is required

This module is THEORY-ONLY:
- No data access
- No execution logic
- No learning
"""

from .vector import PersonalityVector


# -----------------------------
# Canonical Neutral Default
# -----------------------------

NEUTRAL = PersonalityVector(
    D=0.5,  # moderate decay responsiveness
    O=0.5,  # balanced overshoot risk
    E=0.5,  # moderate exit hostility
    R=0.5,  # narrative moderately reliable
)


# -----------------------------
# Domain-Oriented Defaults
# -----------------------------
# These are priors, not guarantees.
# They may be overridden by learned personality later.
# -----------------------------

DEFAULTS_BY_DOMAIN = {
    # Broad, liquid equities
    "equities": PersonalityVector(
        D=0.4,  # intent persists reasonably well
        O=0.3,  # fewer extreme spikes
        E=0.3,  # relatively forgiving exits
        R=0.6,  # narrative often matters
    ),

    # High-narrative, fast-moving AI / tech
    "ai": PersonalityVector(
        D=0.7,  # narrative decays quickly
        O=0.8,  # strong overshoot behavior
        E=0.6,  # exits can be painful
        R=0.7,  # narrative often drives moves
    ),

    # Macro / rates / FX-like behavior
    "macro": PersonalityVector(
        D=0.2,  # intent persists longer
        O=0.2,  # slow, grinding moves
        E=0.2,  # highly liquid exits
        R=0.4,  # narrative less ticker-specific
    ),

    # Speculative / low-liquidity / small-cap
    "speculative": PersonalityVector(
        D=0.9,  # intent decays very fast
        O=0.9,  # extreme spike and snapback risk
        E=0.9,  # hostile exits
        R=0.3,  # narrative unreliable
    ),
}


# -----------------------------
# Helper Accessor
# -----------------------------

def get_default_personality(domain: str) -> PersonalityVector:
    """
    Return the default personality for a given domain.

    Falls back to NEUTRAL if domain is unknown.
    """
    return DEFAULTS_BY_DOMAIN.get(domain.lower(), NEUTRAL)