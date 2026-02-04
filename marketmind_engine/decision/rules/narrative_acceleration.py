from marketmind_engine.decision.rule_result import RuleResult


class NarrativeAccelerationRule:
    """
    Detects accelerating narrative attention across independent sources.
    """

    name = "NarrativeAcceleration"

    def evaluate(self, signal: dict) -> RuleResult:
        """
        Evaluate narrative acceleration from a structured signal.

        Expected signal fields (non-ML, numeric):
        - narrative_mentions_current
        - narrative_mentions_previous
        - narrative_source_count
        """

        current = signal.get("narrative_mentions_current", 0)
        previous = signal.get("narrative_mentions_previous", 0)
        sources = signal.get("narrative_source_count", 0)

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
