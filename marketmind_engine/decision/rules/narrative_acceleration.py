from marketmind_engine.decision.types import RuleResult
from marketmind_engine.decision.state import MarketState


class NarrativeAccelerationRule:
    """
    Detects accelerating narrative attention across independent sources.
    """

    name = "NarrativeAcceleration"

    def evaluate(self, market_state: MarketState) -> RuleResult:
        """
        Evaluate narrative acceleration from normalized MarketState.

        Expected MarketState.narrative fields (pre-normalized upstream):
        - mentions_current
        - mentions_previous
        - source_count
        """

        narrative = market_state.narrative

        current = narrative.mentions_current
        previous = narrative.mentions_previous
        sources = narrative.source_count

        acceleration = current - previous

        triggered = (
            acceleration > 0
            and current >= 3
            and sources >= 2
        )

        confidence = 0.4 if triggered else 0.0

        return RuleResult(
            rule_name=self.name,
            triggered=triggered,
            confidence=confidence,
            details={
                "mentions_current": current,
                "mentions_previous": previous,
                "acceleration": acceleration,
                "source_count": sources,
            },
        )