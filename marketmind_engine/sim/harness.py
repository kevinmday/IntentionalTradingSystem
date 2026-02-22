from typing import Dict

from marketmind_engine.execution.position_snapshot import PositionSnapshot
from marketmind_engine.execution.position import Position
from marketmind_engine.decision.state import MarketState


class TemporalSimulationHarness:
    """
    Deterministic intraday simulation harness.

    Drives:
    - Entry decision evaluation (optional)
    - Macro regime
    - Price evolution
    - Lifecycle evaluation
    - Execution closure

    Fully deterministic.
    """

    def __init__(
        self,
        clock,
        macro_source,
        price_feed,
        orchestrator=None,
        lifecycle_manager=None,
        execution_engine=None,
        positions=None,
        decision_engine=None,
        entry_surface_provider=None,
    ):
        self.clock = clock
        self.macro_source = macro_source
        self.price_feed = price_feed
        self.orchestrator = orchestrator
        self.lifecycle_manager = lifecycle_manager
        self.execution_engine = execution_engine
        self.positions = positions or []

        # Phase-9C optional entry validation
        self.decision_engine = decision_engine
        self.entry_surface_provider = entry_surface_provider

    # --------------------------------------------------

    def step(self):

        # --------------------------------------------------
        # Optional Entry Evaluation (Phase-9C)
        # --------------------------------------------------
        if self.decision_engine and self.entry_surface_provider:

            surfaces = self.entry_surface_provider(self.clock)

            state = MarketState(
                symbol="TEST",
                domain="ai",
                narrative="simulated_narrative",
                fils=0.8,
                ucip=0.9,
                ttcf=0.1,
                fractal_levels=None,
                data_source="sim",
                engine_id="sim",
                timestamp_utc=None,
                engine_time=self.clock.now(),
                ignition_time=surfaces.get("ignition_time"),
                price_delta=surfaces.get("price_delta"),
                volume_ratio=surfaces.get("volume_ratio"),
            )

            result = self.decision_engine.evaluate(state)

            print(f"[t={self.clock.now():>4}] decision={result.decision}")

        # --------------------------------------------------
        # Macro Collection
        # --------------------------------------------------
        macro = self.macro_source.collect()

        if self.orchestrator:
            self.orchestrator.step(macro)

        # --------------------------------------------------
        # Lifecycle Evaluation (Correct Architecture)
        # --------------------------------------------------
        if self.lifecycle_manager and self.positions:

            total_market_value = 0.0
            total_unrealized_pnl = 0.0

            portfolio_positions: Dict[str, Position] = {}

            for p in self.positions:
                current_price = self.price_feed.price(p["symbol"])

                market_value = current_price * p["quantity"]
                unrealized = (
                    (current_price - p["entry_price"]) * p["quantity"]
                )

                total_market_value += market_value
                total_unrealized_pnl += unrealized

                position_obj = Position(
                    symbol=p["symbol"],
                    quantity=p["quantity"],
                    average_entry_price=p["entry_price"],
                    market_value=market_value,
                    unrealized_pnl=unrealized,
                    side="long",  # deterministic sim assumption
                )

                portfolio_positions[p["symbol"]] = position_obj

            snapshot = PositionSnapshot(
                positions=portfolio_positions,
                total_market_value=total_market_value,
                total_unrealized_pnl=total_unrealized_pnl,
            )

            # Sync agents with portfolio
            self.lifecycle_manager.sync_with_portfolio(snapshot)

            # Build deterministic market context map
            context_map: Dict[str, Dict] = {}

            for p in self.positions:
                current_price = self.price_feed.price(p["symbol"])

                context_map[p["symbol"]] = {
                    "price": current_price,
                    "fils": 75,
                    "ttcf": 0.05,
                    "drift": 0.01,
                }

            signals = self.lifecycle_manager.evaluate_all(context_map)

            # Process EXIT signals
            for signal in signals:
                if signal.action == "EXIT":
                    self.positions = [
                        p for p in self.positions
                        if p["symbol"] != signal.symbol
                    ]

        # --------------------------------------------------
        # Advance Deterministic Clock
        # --------------------------------------------------
        self.clock.advance()

    # --------------------------------------------------

    def run(self, steps: int):
        for _ in range(steps):
            self.step()