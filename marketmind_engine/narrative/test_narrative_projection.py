from marketmind_engine.narrative.narrative_adapter import NarrativeAdapter


def test_projection_emits_structured_events():
    adapter = NarrativeAdapter()

    headlines = [
        {"title": "NVDA beats earnings"},
        {"title": "AMD rallies after report"},
    ]

    adapter.inject_headlines(headlines)

    events = adapter.get_projection_events()

    symbols = {event.symbol for event in events}

    assert "NVDA" in symbols
    assert "AMD" in symbols

    for event in events:
        assert event.source == "rss"
        assert event.sentiment == 0.0
        assert event.weight == 1.0