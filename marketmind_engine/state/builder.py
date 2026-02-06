from typing import Mapping, Any

from marketmind_engine.state.contracts import MarketState
from marketmind_engine.adapters.narrative_adapter import NarrativeAdapter
from marketmind_engine.adapters.volatility_adapter import VolatilityAdapter
from marketmind_engine.adapters.liquidity_adapter import LiquidityAdapter


class MarketStateBuilder:
    """
    Sole assembly point for MarketState.
    No interpretation logic allowed.
    """

    def __init__(
        self,
        narrative_adapter: NarrativeAdapter | None = None,
        volatility_adapter: VolatilityAdapter | None = None,
        liquidity_adapter: LiquidityAdapter | None = None,
    ):
        self._narrative_adapter = narrative_adapter
        self._volatility_adapter = volatility_adapter
        self._liquidity_adapter = liquidity_adapter

    def build(self, raw_inputs: Mapping[str, Any]) -> MarketState:
        narrative_ctx = None
        volatility_ctx = None
        liquidity_ctx = None

        if self._narrative_adapter:
            narrative_ctx = self._narrative_adapter.build(
                raw_inputs.get("narrative")
            )

        if self._volatility_adapter:
            volatility_ctx = self._volatility_adapter.evaluate(
                raw_inputs.get("volatility")
            )

        if self._liquidity_adapter:
            liquidity_ctx = self._liquidity_adapter.evaluate(
                **(raw_inputs.get("liquidity") or {})
            )

        return MarketState(
            narrative=narrative_ctx,
            volatility=volatility_ctx,
            liquidity=liquidity_ctx,
        )