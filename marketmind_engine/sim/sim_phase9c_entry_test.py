from marketmind_engine.sim.clock import DeterministicClock
from marketmind_engine.sim.macro_source import SyntheticMacroSource
from marketmind_engine.sim.price_feed import SyntheticPriceFeed
from marketmind_engine.sim.harness import TemporalSimulationHarness
from marketmind_engine.sim.entry_surfaces import DeterministicIgnitionSurface
from marketmind_engine.decision.decision_engine import DecisionEngine


# --------------------------------------------------
# Deterministic setup
# --------------------------------------------------

clock = DeterministicClock(start_ts=0)

# Empty macro schedule
macro = SyntheticMacroSource(schedule=[], clock=clock)

# Provide long enough deterministic price series
price_series = {
    "TEST": [100.0] * 1000  # safe upper bound
}

price_feed = SyntheticPriceFeed(series=price_series, clock=clock)

engine = DecisionEngine()
surface = DeterministicIgnitionSurface()

harness = TemporalSimulationHarness(
    clock=clock,
    macro_source=macro,
    price_feed=price_feed,
    decision_engine=engine,
    entry_surface_provider=surface,
)


# --------------------------------------------------
# Run deterministic timeline
# --------------------------------------------------

for _ in range(10):
    harness.step()
    clock.advance(delta=50)