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

    Phase-1 behavior:
    - If no volatility context is present, rule does NOT block.
    - This rule NEVER allows a buy.
    - It only blocks buys when volatility is expanded.
    """

    name = "VolatilityCompression"

    def evaluate(self, market_state: MarketState) -> RuleResult:
        # --------------------------------------------------
        # Phase-1 guard: no volatility context
        # --------------------------------------------------
        volatility = getattr(market_state, "volatility", None)

        if volatility is None:
            return RuleResult(
                name=self.name,
                triggered=False,
                notes="No volatility context provided",
            )

        volatility_state = volatility.state

        blocked = volatility_state == VolatilityState.EXPANDED

        return RuleResult(
            name=self.name,
            triggered=blocked,
            notes=(
                f"volatility_state={volatility_state.value}"
                if blocked
                else f"volatility_state={volatility_state.value} (not blocking)"
            ),
        )