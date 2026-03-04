from typing import Mapping, Any, Optional
from datetime import datetime

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
        narrative_adapter: Optional[NarrativeAdapter] = None,
        volatility_adapter: Optional[VolatilityAdapter] = None,
        liquidity_adapter: Optional[LiquidityAdapter] = None,
        price_adapter: Optional[Any] = None,
        symbol_resolver: Optional[Any] = None,
    ):
        self._narrative_adapter = narrative_adapter
        self._volatility_adapter = volatility_adapter
        self._liquidity_adapter = liquidity_adapter
        self._price_adapter = price_adapter
        self._symbol_resolver = symbol_resolver

    def build(self, raw_inputs: Mapping[str, Any]) -> MarketState:

        narrative_ctx = None
        volatility_ctx = None
        liquidity_ctx = None

        # --- Narrative ---
        if self._narrative_adapter:
            narrative_ctx = self._narrative_adapter.build(
                raw_inputs.get("narrative")
            )

        # --- Volatility ---
        if self._volatility_adapter:
            volatility_ctx = self._volatility_adapter.evaluate(
                raw_inputs.get("volatility")
            )

        # --- Liquidity ---
        if self._liquidity_adapter:
            liquidity_ctx = self._liquidity_adapter.evaluate(
                **(raw_inputs.get("liquidity") or {})
            )

        # --- Defaults ---
        symbol = None
        domain = None
        price = None
        price_delta = 0.0
        volume_ratio = 1.0

        # Intention metrics baseline
        fils = 0.0
        ucip = 0.0
        ttcf = 0.0

        # Timing
        engine_time = int(datetime.utcnow().timestamp())
        ignition_time = None

        # --- Optional Price Enrichment ---
        if self._symbol_resolver and self._price_adapter:
            text = raw_inputs.get("text")
            if text:
                symbols = self._symbol_resolver.resolve(text)
                if symbols:
                    symbol = symbols[0]
                    domain = "equity"

                    try:
                        metrics = self._price_adapter.get_price_metrics(symbol)
                        price = metrics.get("price")
                        price_delta = metrics.get("price_delta", 0.0)
                        volume_ratio = metrics.get("volume_ratio", 1.0)
                    except Exception:
                        pass

        return MarketState(
            symbol=symbol,
            domain=domain,
            fils=fils,
            ucip=ucip,
            ttcf=ttcf,
            narrative=narrative_ctx,
            engine_time=engine_time,
            ignition_time=ignition_time,
            volatility=volatility_ctx,
            liquidity=liquidity_ctx,
            price=price,
            price_delta=price_delta,
            volume_ratio=volume_ratio,
        )
