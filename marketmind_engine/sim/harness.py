from marketmind_engine.sim.snapshot import SimulatedPositionSnapshot


class TemporalSimulationHarness:
    """
    Deterministic intraday simulation harness.

    Drives:
    - Macro regime
    - Price evolution
    - Lifecycle evaluation
    - Execution closure

    No runtime wiring.
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
    ):
        self.clock = clock
        self.macro_source = macro_source
        self.price_feed = price_feed
        self.orchestrator = orchestrator
        self.lifecycle_manager = lifecycle_manager
        self.execution_engine = execution_engine
        self.positions = positions or []

    def step(self):
        macro = self.macro_source.collect()

        if self.orchestrator:
            self.orchestrator.step(macro)

        # --- Lifecycle evaluation ---
        if self.lifecycle_manager:
            for position in list(self.positions):
                current_price = self.price_feed.price(position["symbol"])

                snapshot = SimulatedPositionSnapshot(
                    symbol=position["symbol"],
                    entry_price=position["entry_price"],
                    current_price=current_price,
                )

                directive = self.lifecycle_manager.evaluate(snapshot)

                if getattr(directive, "exit", False):
                    if self.execution_engine:
                        self.execution_engine.close(position["symbol"])
                    self.positions.remove(position)

        self.clock.advance()

    def run(self, steps: int):
        for _ in range(steps):
            self.step()
