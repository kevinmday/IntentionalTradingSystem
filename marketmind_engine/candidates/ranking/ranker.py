# marketmind_engine/candidates/ranking/ranker.py

from typing import List

from marketmind_engine.candidates.scoring.types import ScoredCandidate


def rank_candidates(candidates: List[ScoredCandidate]) -> List[ScoredCandidate]:
    """
    Phase-6C-A minimal ranker.

    Contract guarantees:
    - Deterministic
    - Stable ordering
    - No mutation of inputs
    - No filtering
    - No priority logic
    """

    # Python's sorted() is stable by design.
    # We sort by score descending only.
    return sorted(
        candidates,
        key=lambda c: c.score,
        reverse=True,
    )