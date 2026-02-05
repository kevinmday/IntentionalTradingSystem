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

        Phase-1 behavior:
        - If narrative is None, rule evaluates cleanly and does NOT trigger.
        """

        narrative = market_state.narrative

        # ---------------------------------------------
        # Phase-1 guard: no narrative means no trigger
        # ---------------------------------------------
        if narrative is None:
            return RuleResult(
                name=self.name,
                triggered=False,
                notes="No narrative context provided",
            )

        current = narrative.mentions_current
        previous = narrative.mentions_previous
        sources = narrative.source_count

        acceleration = current - previous

        triggered = (
            acceleration > 0
            and current >= 3
            and sources >= 2
        )

        return RuleResult(
            name=self.name,
            triggered=triggered,
            notes=(
                f"acceleration={acceleration}, "
                f"current={current}, "
                f"sources={sources}"
            ),
        )