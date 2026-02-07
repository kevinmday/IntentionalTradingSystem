"""
Domain snapshot with ripple propagation (Phase-4D).
"""

from typing import Any, List
from .intention_domain import IntentionDomain
from .asset_ripple import AssetRipple
from .ripple_mapper import map_domain_to_assets


def build_domain_snapshot(
    domain: IntentionDomain,
    context: Any,
) -> List[AssetRipple]:
    """
    Produce asset ripple candidates for a domain.
    """
    return map_domain_to_assets(domain.name, context)