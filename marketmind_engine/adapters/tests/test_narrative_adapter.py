from datetime import datetime, timedelta, timezone

from marketmind_engine.adapters.narrative_adapter import NarrativeAdapter


def make_event(hours_ago, source):
    return {
        "timestamp": datetime.now(timezone.utc) - timedelta(hours=hours_ago),
        "source": source,
    }


def test_no_events():
    adapter = NarrativeAdapter()
    assert adapter.build(None) is None
    assert adapter.build([]) is None


def test_insufficient_sources():
    adapter = NarrativeAdapter(min_sources=2)
    events = [make_event(1, "Reuters")]
    assert adapter.build(events) is None


def test_no_acceleration():
    adapter = NarrativeAdapter()
    events = [
        make_event(5, "Reuters"),
        make_event(4, "AP"),
        make_event(1, "Reuters"),
    ]
    assert adapter.build(events) is None


def test_detects_acceleration():
    adapter = NarrativeAdapter()
    events = [
        make_event(5, "Reuters"),
        make_event(1, "Reuters"),
        make_event(1, "AP"),
        make_event(0.5, "Bloomberg"),
    ]
    ctx = adapter.build(events)
    assert ctx is not None
    assert ctx.accelerating is True
    assert ctx.source_count >= 2


def test_sudden_emergence():
    adapter = NarrativeAdapter()
    events = [
        make_event(1, "Reuters"),
        make_event(1, "AP"),
    ]
    ctx = adapter.build(events)
    assert ctx is not None