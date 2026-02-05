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

    This rule NEVER allows a buy.
    It only blocks buys when liquidity is THIN.
    """

    rule_name = "LiquidityParticipation"

    def evaluate(self, market_state: MarketState) -> RuleResult:
        """
        Expected MarketState.liquidity fields (normalized upstream):
        - state : LiquidityState (THIN | NORMAL | CROWDED)
        """

        liquidity_state = market_state.liquidity.state

        blocked = liquidity_state == LiquidityState.THIN

        return RuleResult(
            rule_name=self.rule_name,
            triggered=blocked,
            confidence=1.0 if blocked else 0.0,
            details={
                "liquidity_state": liquidity_state.value,
                "block_reason": "thin_liquidity" if blocked else None,
            },
        )