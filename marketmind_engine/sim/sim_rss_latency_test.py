from marketmind_engine.decision.decision_engine import DecisionEngine
from marketmind_engine.decision.state import MarketState


def run_latency_test():
    engine = DecisionEngine()

    print("=== RSS → DECISION LATENCY TEST ===")

    # t=0 — baseline, no ignition
    state = MarketState(
        symbol="TEST",
        domain="ai",
        narrative=None,
        fils=0.40,
        ucip=0.35,
        ttcf=0.20,
        fractal_levels=None,
        data_source="sim",
        engine_id="rss-latency",
        timestamp_utc=None,
        engine_time=0,
        ignition_time=None,
        price_delta=0.00,
        volume_ratio=1.0,
    )

    result = engine.evaluate(state)
    print(f"[t=0] decision={result.decision}")

    # t=100 — narrative ignition BEFORE breakout
    state = MarketState(
        symbol="TEST",
        domain="ai",
        narrative="AI breakthrough announced",
        fils=0.90,
        ucip=0.92,
        ttcf=0.05,
        fractal_levels=None,
        data_source="sim",
        engine_id="rss-latency",
        timestamp_utc=None,
        engine_time=100,
        ignition_time=100,
        price_delta=0.01,  # small move only
        volume_ratio=2.2,
    )

    result = engine.evaluate(state)
    print(f"[t=100] decision={result.decision}")

    # t=150 — price breakout AFTER ignition
    state = MarketState(
        symbol="TEST",
        domain="ai",
        narrative="AI breakthrough announced",
        fils=0.85,
        ucip=0.90,
        ttcf=0.07,
        fractal_levels=None,
        data_source="sim",
        engine_id="rss-latency",
        timestamp_utc=None,
        engine_time=150,
        ignition_time=100,
        price_delta=0.09,  # breakout
        volume_ratio=4.0,
    )

    result = engine.evaluate(state)
    print(f"[t=150] decision={result.decision}")

    print("=== END TEST ===")


if __name__ == "__main__":
    run_latency_test()