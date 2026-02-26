from marketmind_engine.agents.lifecycle_manager import AgentLifecycleManager
from marketmind_engine.execution.position_snapshot import PositionSnapshot
from marketmind_engine.execution.position import Position


def test_rss_burst_behavior():

    manager = AgentLifecycleManager(debug_attention=False)

    position = Position(
        symbol="BURST",
        quantity=5,
        average_entry_price=100,
        market_value=500,
        unrealized_pnl=0,
        side="long",
    )

    snapshot = PositionSnapshot(
        positions={"BURST": position},
        total_market_value=500,
        total_unrealized_pnl=0,
    )

    manager.sync_with_portfolio(snapshot)

    # Simulate burst of 50 rapid headlines
    for i in range(50):
        manager.route_rss_event({
            "symbol": "BURST",
            "engine_time": i,
            "source": f"S{i % 5}",  # 5 rotating sources
            "sentiment": 1.0
        })

    attn = manager.get_attention_snapshot("BURST")

    assert attn is not None
    assert attn.density > 0
    assert attn.source_spread == 5 / 50
    assert attn.sentiment_bias == 1.0