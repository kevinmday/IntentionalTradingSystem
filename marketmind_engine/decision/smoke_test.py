"""
MarketState Smoke Test Harness

Runs deterministic MarketState examples through the DecisionEngine.
DEV-ONLY.
"""

from datetime import datetime, timezone
from types import SimpleNamespace

from marketmind_engine.decision.decision_engine import DecisionEngine
from marketmind_engine.decision.state import MarketState


def make_state(
    *,
    fils: float,
    ucip: float,
    ttcf: float,
    domain: str,
) -> MarketState:
    """
    Construct a fully valid MarketState for smoke testing.
    """

    return MarketState(
        # --- Required identity fields ---
        symbol="TEST",
        domain=domain,
        data_source="smoke_test",
        engine_id="SMOKE_ENGINE",
        timestamp_utc=datetime.now(timezone.utc),

        # --- Required structural fields ---
        narrative=SimpleNamespace(),          # minimal stub
        fractal_levels={},                    # empty but valid

        # --- Core intention metrics ---
        fils=fils,
        ucip=ucip,
        ttcf=ttcf,
    )


def run_case(name: str, state: MarketState) -> None:
    print("=" * 60)
    print(f"CASE: {name}")
    print("-" * 60)

    engine = DecisionEngine()
    result = engine.evaluate(state)

    print("Decision:", result.decision)
    print("Rule Results:")
    for r in result.rule_results:
        print(
            f"  - {r.rule_name}: "
            f"triggered={r.triggered}, "
            f"block={r.block}, "
            f"override={r.override}, "
            f"reason={r.reason}"
        )


def main():
    run_case(
        "BASELINE (equities)",
        make_state(
            fils=0.55,
            ucip=0.45,
            ttcf=0.25,
            domain="equities",
        ),
    )

    run_case(
        "HIGH_INTENT (AI domain)",
        make_state(
            fils=0.85,
            ucip=0.80,
            ttcf=0.05,
            domain="ai",
        ),
    )


if __name__ == "__main__":
    main()