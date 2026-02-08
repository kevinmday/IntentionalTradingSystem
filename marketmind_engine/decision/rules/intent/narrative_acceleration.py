"""
Narrative Acceleration Rule

Phase-5 safe:
- Narrative is not yet structured
- Domain name or None must NOT trigger
"""

from marketmind_engine.decision.rules.base import (
    BaseRule,
    RuleCategory,
    RuleResult,
)
from marketmind_engine.decision.state import MarketState


class NarrativeAccelerationRule(BaseRule):
    name = "NarrativeAcceleration"
    category = RuleCategory.INTENT

    def evaluate(self, state: MarketState) -> RuleResult:
        narrative = state.narrative

        # Phase-5 guard
        if narrative is None or isinstance(narrative, str):
            return RuleResult(
                rule_name=self.name,
                category=self.category,
                triggered=False,
            )

        try:
            if (
                narrative.acceleration_score > 0.5
                and narrative.mentions_future > narrative.mentions_current
            ):
                return RuleResult(
                    rule_name=self.name,
                    category=self.category,
                    triggered=True,
                )
        except AttributeError:
            pass

        return RuleResult(
            rule_name=self.name,
            category=self.category,
            triggered=False,
        )