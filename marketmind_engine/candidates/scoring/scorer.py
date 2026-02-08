# marketmind_engine/candidates/scoring/scorer.py

from typing import List

from marketmind_engine.candidates.scoring.types import ScoredCandidate
from marketmind_engine.candidates.scoring.weights import COMPONENT_WEIGHTS


# Canonical Phase-6B component vocabulary
CANONICAL_COMPONENTS = {
    "intention_strength": 0.0,
    "coherence": 0.0,
    "chaos_discount": 0.0,
    "domain_weight": 0.0,
}


# Static, deterministic domain weighting
DOMAIN_WEIGHT_MAP = {
    "AI-Bio": 1.0,
    "Defense": 1.0,
    "Energy": 1.0,
    "Finance": 1.0,
    "Technology": 1.0,
    "Healthcare": 1.0,
}


def _lookup_domain_weight(domain: str) -> float:
    return DOMAIN_WEIGHT_MAP.get(domain, 0.0)


def _compute_coherence(eligible: bool, market_ok: bool) -> float:
    return 1.0 if (eligible and market_ok) else 0.0


def _compute_chaos_discount(market_ok: bool) -> float:
    return 0.0 if market_ok else 1.0


def _compute_intention_strength(candidate) -> float:
    """
    Bounded passthrough from existing ripple magnitude.
    Fails safe if attribute is missing or non-numeric.
    """
    raw = getattr(candidate, "ripple_strength", 0.0)
    try:
        value = float(raw)
    except (TypeError, ValueError):
        value = 0.0

    # Bound to [0.0, 1.0] to prevent dominance
    return max(0.0, min(1.0, value))


def _compute_weighted_score(components: dict) -> float:
    total = 0.0
    for key, value in components.items():
        total += value * COMPONENT_WEIGHTS.get(key, 0.0)
    return total


def score_candidates(candidates) -> List[ScoredCandidate]:
    """
    Phase-6B scorer with all components populated.
    Ranking and priority remain frozen.
    """

    scored = []

    for c in candidates:
        components = dict(CANONICAL_COMPONENTS)

        components["domain_weight"] = _lookup_domain_weight(c.domain)
        components["coherence"] = _compute_coherence(c.eligible, c.market_ok)
        components["chaos_discount"] = _compute_chaos_discount(c.market_ok)
        components["intention_strength"] = _compute_intention_strength(c)

        score = _compute_weighted_score(components)

        scored.append(
            ScoredCandidate(
                domain=c.domain,
                symbol=c.symbol,
                decision=c.decision,
                eligible=c.eligible,
                market_ok=c.market_ok,
                components=components,
                score=score,
                priority="BACKLOG",  # intentionally unchanged
                explanation=(
                    "Score computed as weighted sum. "
                    f"intention_strength={components['intention_strength']} "
                    "(bounded ripple passthrough); "
                    f"coherence={components['coherence']} "
                    "from eligibility and market confirmation; "
                    f"chaos_discount={components['chaos_discount']} "
                    "from market confirmation; "
                    f"domain_weight from static mapping ({c.domain})."
                ),
            )
        )

    return scored