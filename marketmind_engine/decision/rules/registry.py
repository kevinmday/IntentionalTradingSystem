from collections import defaultdict
from typing import Iterable, List

from marketmind_engine.decision.rules.base import (
    BaseRule,
    RuleCategory,
    RuleResult,
)


class RuleRegistry:
    """
    Deterministic rule orchestration layer.
    """

    _CATEGORY_ORDER = [
        RuleCategory.INTENT,
        RuleCategory.HYBRID,
        RuleCategory.CONSTRAINT,
        RuleCategory.PROTECTION,
    ]

    def __init__(self, rules: Iterable[BaseRule] | None = None):
        self._rules_by_category: dict[RuleCategory, list[BaseRule]] = defaultdict(list)

        if rules:
            for rule in rules:
                self.register(rule)

    def register(self, rule: BaseRule) -> None:
        self._rules_by_category[rule.category].append(rule)

    def evaluate(self, state) -> List[RuleResult]:
        results: list[RuleResult] = []

        for category in self._CATEGORY_ORDER:
            for rule in self._rules_by_category.get(category, []):
                results.append(rule.evaluate(state))

        return results