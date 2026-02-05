from dataclasses import dataclass
from typing import Optional

from marketmind_engine.adapters.contracts import NarrativeContext


@dataclass(frozen=True)
class MarketState:
    narrative: Optional[NarrativeContext] = None
    volatility: Optional[object] = None
    liquidity: Optional[object] = None