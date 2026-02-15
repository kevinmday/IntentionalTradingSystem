"""
PHASE-6C CONTRACT TEST — CANDIDATE RANKING & PRIORITIZATION

This test defines ranking invariants ONLY.

No scorer logic.
No materializer.
No domain weighting.
No coherence logic.

If this test fails, Phase-6C ranking is not contract-safe.
"""

from copy import deepcopy

from marketmind_engine.candidates.ranking.ranker import rank_candidates
from marketmind_engine.candidates.scoring.types import ScoredCandidate


def _scored_fixture():
    """
    Deterministic scored candidates for ranking isolation.
    """

    return [
        ScoredCandidate(
            domain="Technology",
            symbol="AAA",
            decision="BUY",
            eligible=True,
            market_ok=True,
            components={},
            score=0.80,
            priority="BACKLOG",
            explanation="",
        ),
        ScoredCandidate(
            domain="Technology",
            symbol="BBB",
            decision="BUY",
            eligible=True,
            market_ok=True,
            components={},
            score=0.95,
            priority="BACKLOG",
            explanation="",
        ),
        ScoredCandidate(
            domain="Technology",
            symbol="CCC",
            decision="BUY",
            eligible=True,
            market_ok=True,
            components={},
            score=0.80,
            priority="BACKLOG",
            explanation="",
        ),
    ]


def test_phase6c_ranking_contract():
    """
    Phase-6C invariants:

    1. Ranking returns a list
    2. Candidate count unchanged
    3. Deterministic ordering
    4. Descending score order
    5. Stable tie handling
    6. Inputs not mutated
    """

    scored = _scored_fixture()

    original_scored = deepcopy(scored)

    ranked = rank_candidates(scored)

    # --- Return type ---
    assert isinstance(ranked, list)

    # --- Length preserved ---
    assert len(ranked) == len(scored)

    # --- Input immutability ---
    assert scored == original_scored

    # --- Determinism ---
    ranked_again = rank_candidates(scored)
    assert ranked == ranked_again

    # --- Descending score ---
    scores = [c.score for c in ranked]
    assert scores == sorted(scores, reverse=True)

    # --- Stable tie behavior ---
    # AAA and CCC both 0.80 → relative order must remain
    tied_symbols_original = [
        c.symbol for c in scored if c.score == 0.80
    ]
    tied_symbols_ranked = [
        c.symbol for c in ranked if c.score == 0.80
    ]

    assert tied_symbols_original == tied_symbols_ranked