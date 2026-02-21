import pytest

from marketmind_engine.sim.harness import TemporalSimulationHarness
from marketmind_engine.sim.clock import DeterministicClock
from marketmind_engine.sim.price_feed import SyntheticPriceFeed
from marketmind_engine.sim.macro_source import SyntheticMacroSource
from marketmind_engine.agents.lifecycle_manager import AgentLifecycleManager


def build_harness(context_builder, price_series=None):

    if price_series is None:
        price_series = [100, 100, 100]

    clock = DeterministicClock(start_ts=0)

    price_feed = SyntheticPriceFeed(
        series={"AAPL": price_series},
        clock=clock
    )

    lifecycle = AgentLifecycleManager()

    macro = SyntheticMacroSource(schedule=[], clock=clock)

    harness = TemporalSimulationHarness(
        clock=clock,
        macro_source=macro,
        price_feed=price_feed,
        lifecycle_manager=lifecycle,
        context_builder=context_builder,
        positions=[{
            "symbol": "AAPL",
            "entry_price": price_series[0],
            "quantity": 1.0,
        }],
    )

    return harness


def test_exit_on_hard_stop():

    def context_builder(symbol, price):
        return {
            "price": price,
            "fils": 75,
            "ttcf": 0.05,
            "drift": 0.01,
        }

    harness = build_harness(
        context_builder,
        price_series=[100, 100, 89]
    )

    harness.run(steps=3)

    assert len(harness.positions) == 0


def test_exit_on_ttcf_inversion():

    def context_builder(symbol, price):
        return {
            "price": price,
            "fils": 75,
            "ttcf": 0.22,
            "drift": 0.01,
        }

    harness = build_harness(context_builder)

    harness.run(steps=3)

    assert len(harness.positions) == 0


def test_exit_on_narrative_decay():

    def context_builder(symbol, price):
        return {
            "price": price,
            "fils": 45,
            "ttcf": 0.05,
            "drift": 0.01,
        }

    harness = build_harness(context_builder)

    harness.run(steps=3)

    assert len(harness.positions) == 0


def test_exit_on_negative_drift():

    def context_builder(symbol, price):
        return {
            "price": price,
            "fils": 75,
            "ttcf": 0.05,
            "drift": -0.01,
        }

    harness = build_harness(context_builder)

    harness.run(steps=3)

    assert len(harness.positions) == 0


def test_hold_when_all_stable():

    def context_builder(symbol, price):
        return {
            "price": price,
            "fils": 75,
            "ttcf": 0.05,
            "drift": 0.01,
        }

    harness = build_harness(context_builder)

    harness.run(steps=3)

    assert len(harness.positions) == 1

