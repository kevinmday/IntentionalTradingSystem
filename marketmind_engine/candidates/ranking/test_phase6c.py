"""
PHASE-6C CONTRACT TEST — CANDIDATE RANKING & PRIORITIZATION

This test defines ranking invariants ONLY.

No priority bands.
No thresholds.
No execution logic.
No score recomputation.

If this test fails, Phase-6C is not contract-safe.
"""

from copy import deepcopy

from marketmind_engine.candidates.scoring.scorer import score_candidates
from marketmind_engine.candidates.materializer import materialize_candidates
from marketmind_engine.candidates.ranking.ranker import rank_candidates


def test_phase6c_ranking_contract():
    """
    Phase-6C invariants:

    1. Phase-6B still works unchanged
    2. Ranking returns a list
    3. Candidate count is unchanged
    4. Ranking is deterministic
    5. Ordering is by descending score
    6. Ties are stable
    7. Inputs are not mutated
    """

    # --- Step 1: Produce scored candidates (Phase-6B precondition) ---
    candidates = materialize_candidates()
    scored = score_candidates(candidates)

    assert len(scored) > 0, "Precondition failed: no scored candidates"

    original_scored = deepcopy(scored)

    # --- Step 2: Rank candidates ---
    ranked = rank_candidates(scored)

    # --- Invariant 1: Return type ---
    assert isinstance(ranked, list), "rank_candidates must return a list"

    # --- Invariant 2: Length preserved ---
    assert len(ranked) == len(scored), "Ranking must not drop or add candidates"

    # --- Invariant 3: Input immutability ---
    assert scored == original_scored, "Ranking must not mutate input candidates"

    # --- Invariant 4: Determinism ---
    ranked_again = rank_candidates(scored)
    assert ranked == ranked_again, "Ranking must be deterministic across runs"

    # --- Invariant 5: Descending score order ---
    scores = [c.score for c in ranked]
    assert scores == sorted(scores, reverse=True), (
        "Candidates must be ordered by descending score"
    )

    # --- Invariant 6: Stable tie-breaking ---
    # For equal scores, original relative order must be preserved
    score_to_symbols = {}
    for c in scored:
        score_to_symbols.setdefault(c.score, []).append(c.symbol)

    ranked_score_to_symbols = {}
    for c in ranked:
        ranked_score_to_symbols.setdefault(c.score, []).append(c.symbol)

    for score, symbols in score_to_symbols.items():
        if len(symbols) > 1:
            assert symbols == ranked_score_to_symbols.get(score), (
                "Ranking must preserve relative order for tied scores"
            )