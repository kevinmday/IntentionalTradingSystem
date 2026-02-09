import pytest

from marketmind_engine.decision.policy_evaluator import PolicyEvaluator
from marketmind_engine.decision.decision_type import DecisionType
from marketmind_engine.decision.rules.base import RuleResult, RuleCategory


def rr(
    category: RuleCategory,
    *,
    triggered: bool = False,
    block: bool = False,
    override: str | None = None,
):
    return RuleResult(
        rule_name="test_rule",
        category=category,
        triggered=triggered,
        block=block,
        override=override,
    )


def test_market_not_confirmed_blocks_everything():
    evaluator = PolicyEvaluator()

    rules = [
        rr(RuleCategory.INTENT, triggered=True),
        rr(RuleCategory.PROTECTION, override="force_stop"),
    ]

    decision = evaluator.evaluate(
        rule_results=rules,
        market_confirmed=False,
    )

    assert decision == DecisionType.BLOCKED


def test_protection_override_supersedes_all():
    evaluator = PolicyEvaluator()

    rules = [
        rr(RuleCategory.INTENT, triggered=True),
        rr(RuleCategory.CONSTRAINT, block=True),
        rr(RuleCategory.PROTECTION, override="emergency"),
    ]

    decision = evaluator.evaluate(
        rule_results=rules,
        market_confirmed=True,
    )

    assert decision == DecisionType.OVERRIDDEN


def test_constraint_violation_blocks_action():
    evaluator = PolicyEvaluator()

    rules = [
        rr(RuleCategory.INTENT, triggered=True),
        rr(RuleCategory.CONSTRAINT, block=True),
    ]

    decision = evaluator.evaluate(
        rule_results=rules,
        market_confirmed=True,
    )

    assert decision == DecisionType.BLOCKED


def test_positive_intent_allows_buy():
    evaluator = PolicyEvaluator()

    rules = [
        rr(RuleCategory.INTENT, triggered=True),
    ]

    decision = evaluator.evaluate(
        rule_results=rules,
        market_confirmed=True,
    )

    assert decision == DecisionType.ALLOW_BUY


def test_no_intent_results_in_no_action():
    evaluator = PolicyEvaluator()

    rules = []

    decision = evaluator.evaluate(
        rule_results=rules,
        market_confirmed=True,
    )

    assert decision == DecisionType.NO_ACTION


def test_untriggered_intent_defers_decision():
    evaluator = PolicyEvaluator()

    rules = [
        rr(RuleCategory.INTENT, triggered=False),
    ]

    decision = evaluator.evaluate(
        rule_results=rules,
        market_confirmed=True,
    )

    assert decision == DecisionType.DEFERRED