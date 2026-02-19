from marketmind_engine.sim.clock import DeterministicClock
from marketmind_engine.sim.price_feed import SyntheticPriceFeed
from marketmind_engine.sim.macro_source import SyntheticMacroSource
from marketmind_engine.sim.harness import TemporalSimulationHarness


class FakeDirective:
    def __init__(self, exit_signal: bool):
        self.exit = exit_signal


class FakeLifecycleManager:
    """
    EXIT if pnl <= -0.05
    """

    def evaluate(self, snapshot):
        if snapshot.pnl_pct <= -0.05:
            return FakeDirective(True)
        return FakeDirective(False)


class FakeExecutionEngine:
    def __init__(self):
        self.closed = []

    def close(self, symbol):
        self.closed.append(symbol)


def run_sim():
    clock = DeterministicClock()

    price_series = {
        "AAPL": [100, 98, 95]  # -5% at ts=2
    }

    feed = SyntheticPriceFeed(price_series, clock)
    macro = SyntheticMacroSource([], clock)

    lifecycle = FakeLifecycleManager()
    execution = FakeExecutionEngine()

    positions = [
        {"symbol": "AAPL", "entry_price": 100}
    ]

    harness = TemporalSimulationHarness(
        clock=clock,
        macro_source=macro,
        price_feed=feed,
        lifecycle_manager=lifecycle,
        execution_engine=execution,
        positions=positions,
    )

    harness.run(3)

    print("Closed positions:", execution.closed)


if __name__ == "__main__":
    run_sim()
