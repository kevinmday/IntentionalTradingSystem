"""
Asset ripple model (Phase-4D).

Represents intention propagation from a domain
into an asset via structural or narrative adjacency.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class AssetRipple:
    symbol: str
    domain: str
    strength: float          # [0.0–1.0] ripple coupling strength
    reason: Optional[str] = None