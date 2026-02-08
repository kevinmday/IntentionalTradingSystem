"""
Liquidity Participation Rule

Phase-5 safe:
- Liquidity is a float
- Structured liquidity state arrives in Phase-6
"""

from marketmind_engine.decision.types import RuleResult
from marketmind_engine.decision.state import MarketState


class LiquidityParticipationRule:
    name = "LiquidityParticipation"

    def evaluate(self, state: MarketState) -> RuleResult | None:
        """
        Evaluate whether market participation is sufficient.

        Phase-5 behavior:
        - Accept float liquidity
        - Never block (no structure yet)
        """

        liquidity = state.liquidity

        # ----------------------------------------------
        # Phase-5 guard: primitive liquidity
        # ----------------------------------------------
        if liquidity is None or isinstance(liquidity, (int, float)):
            return RuleResult(
                name=self.name,
                triggered=False,
            )

        # ----------------------------------------------
        # Future structured liquidity path (Phase-6)
        # ----------------------------------------------
        try:
            if liquidity.state == "INSUFFICIENT":
                return RuleResult(
                    name=self.name,
                    triggered=True,
                )
        except AttributeError:
            pass

        return RuleResult(
            name=self.name,
            triggered=False,
        )