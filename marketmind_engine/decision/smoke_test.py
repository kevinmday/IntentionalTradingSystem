"""
MarketState Smoke Test Harness

Runs deterministic MarketState examples through the DecisionEngine.

DEV-ONLY. Works with frozen MarketState dataclass.
"""

from types import SimpleNamespace

from marketmind_engine.decision.decision_engine import DecisionEngine
from marketmind_engine.decision.state import MarketState


def make_state(
    *,
    fils: float,
    ucip: float,
    ttcf: float,
    mentions_current: int,
    mentions_previous: int,
    source_count: int,
    volatility_state: str,
    liquidity_state: str,
) -> MarketState:
    """
    Create a MarketState compatible with frozen dataclass constraints.
    """

    # Construct with required core fields
    state = MarketState(
        ucip=ucip,
        fils=fils,
        ttcf=ttcf,
    )

    # Inject derived / normalized fields safely (frozen dataclass pattern)
    object.__setattr__(
        state,
        "narrative",
        SimpleNamespace(
            mentions_current=mentions_current,
            mentions_previous=mentions_previous,
            source_count=source_count,
        ),
    )

    object.__setattr__(
        state,
        "volatility",
        SimpleNamespace(
            state=volatility_state,
        ),
    )

    object.__setattr__(
        state,
        "liquidity",
        SimpleNamespace(
            state=liquidity_state,
        ),
    )

    return state


def run_case(name: str, state: MarketState) -> None:
    print("=" * 60)
    print(f"CASE: {name}")
    print("-" * 60)

    engine = DecisionEngine()
    result = engine.evaluate(state)

    print(f"Decision: {result.decision}")
    print("Rule Results:")
    for r in result.rule_results:
        print(
            f"  - {r.rule_name}: "
            f"triggered={r.triggered}, "
            f"confidence={r.confidence}, "
            f"details={r.details}"
        )


def main():
    run_case(
        "ALLOW_BUY (Intent + Capacity + Participation)",
        make_state(
            fils=0.7,
            ucip=0.6,
            ttcf=0.2,
            mentions_current=5,
            mentions_previous=2,
            source_count=3,
            volatility_state="compressed",
            liquidity_state="normal",
        ),
    )

    run_case(
        "BLOCK (Volatility Expanded)",
        make_state(
            fils=0.7,
            ucip=0.3,
            ttcf=0.2,
            mentions_current=6,
            mentions_previous=3,
            source_count=3,
            volatility_state="expanded",
            liquidity_state="normal",
        ),
    )

    run_case(
        "BLOCK (Thin Liquidity)",
        make_state(
            fils=0.7,
            ucip=0.6,
            ttcf=0.1,
            mentions_current=6,
            mentions_previous=3,
            source_count=3,
            volatility_state="compressed",
            liquidity_state="thin",
        ),
    )


if __name__ == "__main__":
    main()