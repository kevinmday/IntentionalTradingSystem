from datetime import datetime
from typing import List

from marketmind_engine.decision.state import MarketState
from marketmind_engine.narrative.feed_aggregator import NarrativeItem


class NarrativeStateAdapter:
    """
    Converts NarrativeItem objects into MarketState instances.

    Natural deterministic mapping.
    No forced ignition.
    No price data.
    No capital logic.
    """

    def __init__(self, engine_id="narrative-intake"):
        self.engine_id = engine_id

    def convert(self, items: List[NarrativeItem]) -> List[MarketState]:
        states = []

        for item in items:

            # ---------------------------------------------
            # Deterministic weight-based mapping
            # ---------------------------------------------
            weight = item.weight if item.weight is not None else 1.0

            # Conservative narrative strength scaling
            fils = min(1.0, 0.5 * weight)
            ucip = min(1.0, 0.6 * weight)

            # Baseline low chaos assumption for fresh narrative
            ttcf = 0.1

            state = MarketState(
                symbol=None,
                domain=item.domain,
                narrative=item.title,
                fils=fils,
                ucip=ucip,
                ttcf=ttcf,
                fractal_levels=None,
                data_source="rss",
                engine_id=self.engine_id,
                timestamp_utc=datetime.utcnow().isoformat(),
                liquidity=None,
                volatility=None,
                responsiveness=None,
                engine_time=0,
                ignition_time=0,
                price_delta=0.0,
                volume_ratio=1.0,
            )

            states.append(state)

        return states