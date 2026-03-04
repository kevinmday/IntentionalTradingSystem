from typing import Optional

from marketmind_engine.execution.execution_input import ExecutionInput
from marketmind_engine.decision.state import MarketState


class ExecutionInputFactory:
    """
    Responsible for assembling a full ExecutionInput snapshot
    from system services for a given symbol.

    This class performs NO decision logic.
    It strictly constructs immutable execution snapshots.
    """

    def __init__(
        self,
        regime_service,
        policy_engine,
        capital_service,
        position_service,
        price_service,
        clock,
    ):
        self.regime_service = regime_service
        self.policy_engine = policy_engine
        self.capital_service = capital_service
        self.position_service = position_service
        self.price_service = price_service
        self.clock = clock

        # 🔹 Deterministic price memory (per symbol)
        self._last_price_by_symbol = {}

    # -------------------------------------------------------------
    # Public Entry
    # -------------------------------------------------------------

    def build_for_symbol(self, symbol: str) -> ExecutionInput:
        """
        Build a complete ExecutionInput snapshot for a symbol.
        """

        engine_time = self.clock.now()

        # 1️⃣ Build MarketState
        market_state = self._build_market_state(symbol, engine_time)

        # 2️⃣ Evaluate Policy
        policy_result = self.policy_engine.evaluate(market_state)

        # 3️⃣ Snapshot Capital
        capital_snapshot = self.capital_service.snapshot()

        # 4️⃣ Snapshot Position
        position_snapshot = self.position_service.snapshot(symbol)

        # 5️⃣ Current Price
        current_price = self.price_service.get_price(symbol)

        return ExecutionInput(
            policy_result=policy_result,
            market_state=market_state,
            capital_snapshot=capital_snapshot,
            position_snapshot=position_snapshot,
            current_price=current_price,
            engine_time=engine_time,
            stop_price=None,
        )

    # -------------------------------------------------------------
    # Internal Builders
    # -------------------------------------------------------------

    def _build_market_state(self, symbol: str, engine_time) -> MarketState:
        """
        Construct MarketState using available services.

        Keep minimal for now.
        Extend only when needed.
        """

        current_price = self.price_service.get_price(symbol)
        regime_state = self.regime_service.current_state()

        # 🔹 Compute deterministic price delta
        previous_price = self._last_price_by_symbol.get(symbol)

        if previous_price is None:
            price_delta = 0.0
        else:
            price_delta = current_price - previous_price

        # Update memory for next cycle
        self._last_price_by_symbol[symbol] = current_price

        # Placeholder values — narrative wiring comes later
        fils = 0.0
        ucip = 0.0
        ttcf = 0.0

        return MarketState(
            symbol=symbol,
            domain=regime_state.domain if hasattr(regime_state, "domain") else "unknown",
            narrative=None,
            fils=fils,
            ucip=ucip,
            ttcf=ttcf,
            fractal_levels=None,
            data_source="runtime",
            engine_id="paper-runtime",
            timestamp_utc=None,
            engine_time=engine_time,
            ignition_time=0,
            price_delta=price_delta,
            volume_ratio=1.0,
        )
