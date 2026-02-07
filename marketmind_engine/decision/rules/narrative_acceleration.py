"""
Narrative Acceleration Rule

Phase-5 safe:
- Narrative is not yet structured
- Domain name or None must NOT trigger
"""

from marketmind_engine.decision.types import RuleResult
from marketmind_engine.decision.state import MarketState


class NarrativeAccelerationRule:
    name = "NarrativeAcceleration"

    def evaluate(self, state: MarketState) -> RuleResult | None:
        """
        Evaluate narrative acceleration.

        In Phase-5, narrative is expected to be:
        - None
        - str (domain label)

        Structured narrative comes later.
        """

        narrative = state.narrative

        # ----------------------------------------------
        # Phase-5 guard: no structured narrative yet
        # ----------------------------------------------
        if narrative is None or isinstance(narrative, str):
            return RuleResult(
                name=self.name,
                triggered=False,
            )

        # ----------------------------------------------
        # Future-proof path (won't execute yet)
        # ----------------------------------------------
        try:
            if (
                narrative.acceleration_score > 0.5
                and narrative.mentions_future > narrative.mentions_current
            ):
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