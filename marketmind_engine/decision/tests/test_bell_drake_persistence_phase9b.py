import pytest

from marketmind_engine.decision.types import DecisionResult
from marketmind_engine.decision.rules.base import RuleResult, RuleCategory
from marketmind_engine.decision.persistence.evaluator import PersistentDecisionEvaluator


def make_stub_rule_result(name: str, triggered: bool) -> RuleResult:
    """
    Minimal, valid RuleResult stub.
    No rule execution logic required.
    """
    return RuleResult(
        rule_name=name,
        category=RuleCategory.INTENT,
        triggered=triggered,
        reason="stub"
    )


def test_phase9b_decision_result_persistence_roundtrip(tmp_path):
    """
    Phase-9B:
    Verify DecisionResult persistence using real engine types only.
    """

    # --- Arrange ---
    rule_results = [
        make_stub_rule_result("intent_present", True),
        make_stub_rule_result("capacity_sufficient", True),
        make_stub_rule_result("participation_valid", True),
    ]

    decision = DecisionResult(
        decision="ALLOW_BUY",
        rule_results=rule_results,
    )

    evaluator = PersistentDecisionEvaluator(
        storage_path=tmp_path
    )

    # --- Act ---
    evaluator.persist(decision)
    restored = evaluator.load_latest()

    # --- Assert ---
    assert isinstance(restored, DecisionResult)

    assert restored.decision == decision.decision
    assert len(restored.rule_results) == len(decision.rule_results)

    for original, loaded in zip(decision.rule_results, restored.rule_results):
        assert original.rule_name == loaded.rule_name
        assert original.category == loaded.category
        assert original.triggered == loaded.triggered