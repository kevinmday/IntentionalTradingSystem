from datetime import datetime
from typing import List

from marketmind_engine.decision.state import MarketState
from marketmind_engine.narrative.feed_aggregator import NarrativeItem


class NarrativeStateAdapter:
    """
    Converts NarrativeItem objects into MarketState instances.

    IGNITION TEST MODE:
    Forces high-coherence values to validate Bell-Drake trigger path.

    No price data.
    No capital logic.
    Deterministic.
    """

    def __init__(self, engine_id="narrative-intake"):
        self.engine_id = engine_id

    def convert(self, items: List[NarrativeItem]) -> List[MarketState]:
        states = []

        for item in items:

            # --------------------------------------------------
            # Controlled ignition values (force Bell-Drake test)
            # --------------------------------------------------
            fils = 0.85
            ucip = 0.90
            ttcf = 0.05  # low chaos

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
                engine_time=10,
                ignition_time=0,
                price_delta=0.02,
                volume_ratio=1.5,
            )

            states.append(state)

        return states