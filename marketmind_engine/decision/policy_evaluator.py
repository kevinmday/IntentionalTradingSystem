from typing import List

from marketmind_engine.decision.decision_type import DecisionType
from marketmind_engine.decision.rules.base import RuleResult, RuleCategory


class PolicyEvaluator:
    """
    Interprets rule signals and market gates into a single semantic decision.

    Deterministic
    Stateless
    Side-effect free
    """

    def evaluate(
        self,
        rule_results: List[RuleResult],
        market_confirmed: bool,
    ) -> DecisionType:
        # 1. Market gate
        if not market_confirmed:
            return DecisionType.BLOCKED

        # Normalize rule results by category (order-independent)
        by_category = {
            RuleCategory.PROTECTION: [],
            RuleCategory.CONSTRAINT: [],
            RuleCategory.INTENT: [],
        }

        for rr in rule_results:
            if rr.category in by_category:
                by_category[rr.category].append(rr)

        # 2. Protection override
        for rr in by_category[RuleCategory.PROTECTION]:
            if rr.override is not None:
                return DecisionType.OVERRIDDEN

        # 3. Constraint violation
        for rr in by_category[RuleCategory.CONSTRAINT]:
            if rr.block:
                return DecisionType.BLOCKED

        # 4. Intent evaluation
        intent_results = by_category[RuleCategory.INTENT]

        if not intent_results:
            return DecisionType.NO_ACTION

        any_triggered = False
        any_untriggered = False

        for rr in intent_results:
            if rr.triggered:
                any_triggered = True
            else:
                any_untriggered = True

        if any_triggered:
            return DecisionType.ALLOW_BUY

        if any_untriggered:
            return DecisionType.DEFERRED

        # 5. Default
        return DecisionType.NO_ACTION