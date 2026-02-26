from marketmind_engine.agents.lifecycle_manager import AgentLifecycleManager
from marketmind_engine.execution.position_snapshot import PositionSnapshot
from marketmind_engine.execution.position import Position


def test_rss_replay_into_active_agent():

    # -------------------------------------------------
    # 1. Create lifecycle manager
    # -------------------------------------------------

    manager = AgentLifecycleManager()

    # -------------------------------------------------
    # 2. Create synthetic open position
    # -------------------------------------------------

    position = Position(
        symbol="TEST",
        quantity=10,
        average_entry_price=100,
        market_value=1000,
        unrealized_pnl=0,
        side="long",
    )

    snapshot = PositionSnapshot(
        positions={"TEST": position},
        total_market_value=1000,
        total_unrealized_pnl=0,
    )

    manager.sync_with_portfolio(snapshot)

    # Ensure agent exists
    assert "TEST" in manager.active_symbols()

    # -------------------------------------------------
    # 3. Inject deterministic RSS events
    # -------------------------------------------------

    events = [
        {"symbol": "TEST", "engine_time": 1, "source": "A", "sentiment": 0.5},
        {"symbol": "TEST", "engine_time": 2, "source": "B", "sentiment": 1.0},
        {"symbol": "TEST", "engine_time": 3, "source": "A", "sentiment": 0.0},
    ]

    for event in events:
        manager.route_rss_event(event)

    # -------------------------------------------------
    # 4. Inspect attention snapshot
    # -------------------------------------------------

    snapshot = manager.get_attention_snapshot("TEST")

    assert snapshot is not None
    assert snapshot.density > 0
    assert snapshot.source_spread == 2 / 3
    assert snapshot.sentiment_bias == (0.5 + 1.0 + 0.0) / 3