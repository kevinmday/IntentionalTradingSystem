# marketmind_engine/state/builder.py

from typing import Mapping, Any

from marketmind_engine.state.contracts import MarketState
from marketmind_engine.adapters.narrative_adapter import NarrativeAdapter


class MarketStateBuilder:
    def __init__(self, narrative_adapter: NarrativeAdapter | None = None):
        self._narrative_adapter = narrative_adapter

    def build(self, raw_inputs: Mapping[str, Any]) -> MarketState:
        narrative_ctx = None

        if self._narrative_adapter:
            narrative_ctx = self._narrative_adapter.build(
                raw_inputs.get("narrative")
            )

        return MarketState(
            narrative=narrative_ctx,
            volatility=None,
            liquidity=None,
        )