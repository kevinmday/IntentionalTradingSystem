import pytest

from marketmind_engine.attention.symbol_attention_profile import (
    SymbolAttentionProfile,
)


def test_empty_snapshot_returns_zero():
    profile = SymbolAttentionProfile("TEST", window_size=10)
    snapshot = profile.snapshot()

    assert snapshot.density == 0.0
    assert snapshot.velocity == 0.0
    assert snapshot.source_spread == 0.0
    assert snapshot.sentiment_bias == 0.0


def test_basic_ingestion_metrics():
    profile = SymbolAttentionProfile("TEST", window_size=10)

    profile.ingest({"engine_time": 1, "source": "A", "sentiment": 0.5})
    profile.ingest({"engine_time": 2, "source": "B", "sentiment": 1.0})

    snapshot = profile.snapshot()

    assert snapshot.density == 2 / 10
    assert snapshot.velocity == 2 / 10
    assert snapshot.source_spread == 2 / 2
    assert snapshot.sentiment_bias == pytest.approx(0.75)


def test_source_spread_with_duplicates():
    profile = SymbolAttentionProfile("TEST", window_size=10)

    profile.ingest({"engine_time": 1, "source": "A", "sentiment": 0.2})
    profile.ingest({"engine_time": 2, "source": "A", "sentiment": 0.4})
    profile.ingest({"engine_time": 3, "source": "B", "sentiment": 0.6})

    snapshot = profile.snapshot()

    assert snapshot.source_spread == 2 / 3


def test_window_rollover_respects_maxlen():
    profile = SymbolAttentionProfile("TEST", window_size=3)

    profile.ingest({"engine_time": 1, "source": "A", "sentiment": 0.1})
    profile.ingest({"engine_time": 2, "source": "B", "sentiment": 0.2})
    profile.ingest({"engine_time": 3, "source": "C", "sentiment": 0.3})
    profile.ingest({"engine_time": 4, "source": "D", "sentiment": 0.4})

    snapshot = profile.snapshot()

    # Only last 3 events should remain
    assert snapshot.density == 3 / 3
    assert snapshot.velocity == 3 / 3
    assert snapshot.sentiment_bias == pytest.approx((0.2 + 0.3 + 0.4) / 3)
