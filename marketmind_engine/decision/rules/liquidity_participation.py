from enum import Enum

from marketmind_engine.decision.types import RuleResult
from marketmind_engine.decision.state import MarketState


class LiquidityState(Enum):
    THIN = "thin"
    NORMAL = "normal"
    CROWDED = "crowded"


class LiquidityParticipationRule:
    """
    Decision Rule 3

    Determines whether there is sufficient market participation
    for intent and structure to express meaningfully.

    Phase-1 behavior:
    - If no liquidity context is present, rule does NOT block.
    - This rule NEVER allows a buy.
    - It only blocks buys when liquidity is THIN.
    """

    name = "LiquidityParticipation"

    def evaluate(self, market_state: MarketState) -> RuleResult:
        # --------------------------------------------------
        # Phase-1 guard: no liquidity context
        # --------------------------------------------------
        liquidity = getattr(market_state, "liquidity", None)

        if liquidity is None:
            return RuleResult(
                name=self.name,
                triggered=False,
                notes="No liquidity context provided",
            )

        liquidity_state = liquidity.state

        blocked = liquidity_state == LiquidityState.THIN

        return RuleResult(
            name=self.name,
            triggered=blocked,
            notes=(
                f"liquidity_state={liquidity_state.value}"
                if blocked
                else f"liquidity_state={liquidity_state.value} (not blocking)"
            ),
        )