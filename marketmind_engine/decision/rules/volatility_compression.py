"""
Volatility Compression Rule

Phase-5 safe:
- Volatility is a float
- Structured volatility state arrives in Phase-6
"""

from marketmind_engine.decision.types import RuleResult
from marketmind_engine.decision.state import MarketState


class VolatilityCompressionRule:
    name = "VolatilityCompression"

    def evaluate(self, state: MarketState) -> RuleResult | None:
        """
        Evaluate volatility compression.

        Phase-5 behavior:
        - Accept float volatility
        - Never trigger (structure not present yet)
        """

        volatility = state.volatility

        # ----------------------------------------------
        # Phase-5 guard: primitive volatility
        # ----------------------------------------------
        if volatility is None or isinstance(volatility, (int, float)):
            return RuleResult(
                name=self.name,
                triggered=False,
            )

        # ----------------------------------------------
        # Future structured volatility path
        # ----------------------------------------------
        try:
            if volatility.state == "COMPRESSED":
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