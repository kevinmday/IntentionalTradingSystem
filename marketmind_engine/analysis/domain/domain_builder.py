"""
IntentionDomain builder (Phase-4C).

Creates domain objects from narrative context.
"""

from typing import Any
from .intention_domain import IntentionDomain
from .domain_fils import compute_domain_fils


def build_intention_domain(
    name: str,
    context: Any,
) -> IntentionDomain:
    """
    Build a domain-level intention snapshot.
    """
    fils = compute_domain_fils(context)

    return IntentionDomain(
        name=name,
        fils=fils,
        ucip=None,   # wired later
        ttcf=None,   # wired later
        narratives=None,
        confidence=None,
    )