from __future__ import annotations

from dataclasses import dataclass

from marketmind_engine.decision.state import MarketState
from marketmind_engine.decision.rules.base import (
    BaseRule,
    RuleCategory,
    RuleResult,
)


@dataclass(frozen=True)
class NarrativePriceLatencyRule(BaseRule):
    """
    Narrative–Price Latency Constraint (Phase-9C)

    Purpose:
    Confirm narrative ignition couples to price + volume
    within a strict early-session latency window.

    Deterministic.
    Stateless.
    Replay-safe.
    No time calls.
    No mutation.
    """

    name: str = "NarrativePriceLatency"
    category: RuleCategory = RuleCategory.CONSTRAINT

    # --------------------------------------------------
    # Locked deterministic parameters
    # --------------------------------------------------
    window_seconds: int = 300          # 5 minutes
    price_threshold: float = 0.01      # 1% displacement
    volume_threshold: float = 1.2      # 20% above baseline

    def evaluate(self, state: MarketState) -> RuleResult:

        # --------------------------------------------------
        # Guard: ignition must exist
        # --------------------------------------------------
        if state.ignition_time is None:
            return RuleResult(
                rule_name=self.name,
                category=self.category,
                triggered=False,
                block=False,
                reason="IGNITION_ABSENT",
            )

        # --------------------------------------------------
        # Guard: required surfaces must exist
        # --------------------------------------------------
        if (
            state.engine_time is None
            or state.price_delta is None
            or state.volume_ratio is None
        ):
            return RuleResult(
                rule_name=self.name,
                category=self.category,
                triggered=False,
                block=False,
                reason="LATENCY_DATA_INCOMPLETE",
            )

        # --------------------------------------------------
        # Compute latency
        # --------------------------------------------------
        latency = state.engine_time - state.ignition_time

        # If negative, treat as invalid state (defensive but deterministic)
        if latency < 0:
            return RuleResult(
                rule_name=self.name,
                category=self.category,
                triggered=False,
                block=True,
                reason=f"INVALID_LATENCY latency={latency}",
            )

        # --------------------------------------------------
        # Window expiration
        # --------------------------------------------------
        if latency > self.window_seconds:
            return RuleResult(
                rule_name=self.name,
                category=self.category,
                triggered=False,
                block=True,
                reason=f"LATENCY_WINDOW_EXCEEDED latency={latency}s > {self.window_seconds}s",
            )

        # --------------------------------------------------
        # Coupling confirmation
        # --------------------------------------------------
        if (
            state.price_delta >= self.price_threshold
            and state.volume_ratio >= self.volume_threshold
        ):
            return RuleResult(
                rule_name=self.name,
                category=self.category,
                triggered=True,
                block=False,
                reason=(
                    f"COUPLING_CONFIRMED "
                    f"latency={latency}s "
                    f"price_delta={state.price_delta:.4f} "
                    f"volume_ratio={state.volume_ratio:.2f}"
                ),
            )

        # --------------------------------------------------
        # Coupling failure (within window but insufficient displacement)
        # --------------------------------------------------
        return RuleResult(
            rule_name=self.name,
            category=self.category,
            triggered=False,
            block=True,
            reason=(
                f"LATENCY_FAIL "
                f"latency={latency}s "
                f"price_delta={state.price_delta:.4f} "
                f"volume_ratio={state.volume_ratio:.2f}"
            ),
        )