"""
Phase-5A: Project AssetRipples into MarketState
with UCIP and TTCF layered in.

No execution. No price. No indicators.
"""

from typing import List
from marketmind_engine.decision.state import MarketState
from .asset_ripple import AssetRipple
from .intention_domain import IntentionDomain


def project_ripples_to_marketstate(
    domain: IntentionDomain,
    ripples: List[AssetRipple],
) -> List[MarketState]:
    """
    Project domain intention, coherence, and chaos
    through asset ripples into MarketState objects.
    """
    states: List[MarketState] = []

    for ripple in ripples:
        strength = ripple.strength

        asset_fils = domain.fils * strength

        asset_ucip = (
            domain.ucip * strength
            if domain.ucip is not None
            else None
        )

        asset_ttcf = (
            domain.ttcf * strength
            if domain.ttcf is not None
            else None
        )

        states.append(
            MarketState(
                symbol=ripple.symbol,
                fils=asset_fils,
                ucip=asset_ucip,
                ttcf=asset_ttcf,
                narrative=domain.name,
                fractal_levels=None,
                data_source="domain_ripple",
                engine_id=None,
                timestamp_utc=None,
            )
        )

    return states