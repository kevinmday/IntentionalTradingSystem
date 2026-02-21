import pytest

from marketmind_engine.decision.rules.constraint.narrative_price_latency import (
    NarrativePriceLatencyRule,
)
from marketmind_engine.decision.state import MarketState


def make_state(
    ignition_time=None,
    engine_time=None,
    price_delta=None,
    volume_ratio=None,
):
    return MarketState(
        symbol="TEST",
        domain="ai",
        narrative="test",
        fils=0.8,
        ucip=0.9,
        ttcf=0.1,
        fractal_levels=None,
        data_source="unit",
        engine_id="test",
        timestamp_utc=None,
        engine_time=engine_time,
        ignition_time=ignition_time,
        price_delta=price_delta,
        volume_ratio=volume_ratio,
    )


def test_no_ignition_abstains():
    rule = NarrativePriceLatencyRule()
    state = make_state()

    result = rule.evaluate(state)

    assert result.block is False
    assert result.triggered is False
    assert result.reason == "IGNITION_ABSENT"


def test_within_window_and_coupled():
    rule = NarrativePriceLatencyRule()

    state = make_state(
        ignition_time=0,
        engine_time=200,
        price_delta=0.02,
        volume_ratio=1.5,
    )

    result = rule.evaluate(state)

    assert result.block is False
    assert result.triggered is True


def test_price_too_small_blocks():
    rule = NarrativePriceLatencyRule()

    state = make_state(
        ignition_time=0,
        engine_time=200,
        price_delta=0.005,
        volume_ratio=1.5,
    )

    result = rule.evaluate(state)

    assert result.block is True
    assert result.triggered is False


def test_volume_too_small_blocks():
    rule = NarrativePriceLatencyRule()

    state = make_state(
        ignition_time=0,
        engine_time=200,
        price_delta=0.02,
        volume_ratio=1.0,
    )

    result = rule.evaluate(state)

    assert result.block is True
    assert result.triggered is False


def test_window_expired_blocks():
    rule = NarrativePriceLatencyRule()

    state = make_state(
        ignition_time=0,
        engine_time=400,
        price_delta=0.02,
        volume_ratio=1.5,
    )

    result = rule.evaluate(state)

    assert result.block is True
    assert result.reason.startswith("LATENCY_WINDOW_EXCEEDED")


def test_negative_latency_blocks():
    rule = NarrativePriceLatencyRule()

    state = make_state(
        ignition_time=300,
        engine_time=200,
        price_delta=0.02,
        volume_ratio=1.5,
    )

    result = rule.evaluate(state)

    assert result.block is True
    assert result.reason.startswith("INVALID_LATENCY")


def test_boundary_conditions_pass():
    rule = NarrativePriceLatencyRule()

    state = make_state(
        ignition_time=0,
        engine_time=300,
        price_delta=0.01,
        volume_ratio=1.2,
    )

    result = rule.evaluate(state)

    assert result.block is False