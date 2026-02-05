from enum import Enum

from marketmind_engine.decision.types import RuleResult
from marketmind_engine.decision.state import MarketState


class VolatilityState(Enum):
    COMPRESSED = "compressed"
    NEUTRAL = "neutral"
    EXPANDED = "expanded"


class VolatilityCompressionRule:
    """
    Decision Rule 2

    Determines whether market structure (volatility)
    permits price movement in response to intent.

    This rule NEVER allows a buy.
    It only blocks buys when volatility is expanded.
    """

    rule_id = "VolatilityCompressionRule"

    def evaluate(self, market_state: MarketState) -> RuleResult:
        volatility_state = market_state.volatility.state

        blocked = volatility_state == VolatilityState.EXPANDED

        return RuleResult(
            rule_name=self.rule_id,
            triggered=blocked,
            confidence=1.0 if blocked else 0.0,
            details={
                "volatility_state": volatility_state.value,
                "block_reason": "expanded" if blocked else None,
            },
        )