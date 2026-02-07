"""
Domain-level FILS computation (Phase-4C).

Aggregates narrative micro-intentions into
a domain-level FILS score.
"""

from typing import Any
from marketmind_engine.analysis.fils.narrative_adapter import (
    extract_narrative_micro_intentions,
)
from marketmind_engine.analysis.equations.fils_numeric import compute_fils


def compute_domain_fils(domain_context: Any) -> float:
    """
    Compute FILS for an intention domain.

    Narrative-first. No asset data allowed here.
    """
    micro = extract_narrative_micro_intentions(domain_context)
    return compute_fils(micro)