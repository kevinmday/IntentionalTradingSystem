from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from marketmind_engine.decision.state import MarketState
from marketmind_engine.decision.rules.base import (
    BaseRule,
    RuleCategory,
    RuleResult,
)

# ------------------------------------------------------------
# Domain-specific Bell-Drake profiles
# ------------------------------------------------------------

DOMAIN_PROFILES: Dict[str, dict] = {
    "ai": {
        "alpha": 1.3,
        "beta": 1.1,
        "gamma": 0.8,
        "threshold": 0.45,
    },
    "biotech": {
        "alpha": 1.0,
        "beta": 1.4,
        "gamma": 1.2,
        "threshold": 0.55,
    },
    "defense": {
        "alpha": 0.9,
        "beta": 1.6,
        "gamma": 1.3,
        "threshold": 0.65,
    },
    "crypto": {
        "alpha": 1.5,
        "beta": 0.9,
        "gamma": 1.8,
        "threshold": 0.60,
    },
    "financials": {
        "alpha": 0.8,
        "beta": 1.5,
        "gamma": 1.4,
        "threshold": 0.60,
    },
    "consumer": {
        "alpha": 0.7,
        "beta": 1.2,
        "gamma": 1.1,
        "threshold": 0.70,
    },
}


@dataclass(frozen=True)
class BellDrakeThreshold(BaseRule):
    """
    Bell-Drake Coherence Threshold (Domain-Aware)

    Detects emergence of coherent intent from noise.
    Deterministic, stateless, explainable.
    """

    name: str = "BellDrakeThreshold"
    category: RuleCategory = RuleCategory.INTENT

    default_alpha: float = 1.0
    default_beta: float = 1.0
    default_gamma: float = 1.0
    default_threshold: float = 0.60

    def evaluate(self, state: MarketState) -> RuleResult:
        domain = (state.domain or "unknown").lower()
        profile = DOMAIN_PROFILES.get(domain, {})

        alpha = profile.get("alpha", self.default_alpha)
        beta = profile.get("beta", self.default_beta)
        gamma = profile.get("gamma", self.default_gamma)
        threshold = profile.get("threshold", self.default_threshold)

        coherence = (
            (state.fils ** alpha)
            * (state.ucip ** beta)
            * ((1.0 - state.ttcf) ** gamma)
        )

        triggered = coherence >= threshold

        return RuleResult(
            rule_name=self.name,
            category=self.category,
            triggered=triggered,
            score_delta=coherence,
            block=False,
            override=None,
            reason=(
                f"coherence={coherence:.3f} ≥ {threshold:.3f} (domain={domain})"
                if triggered
                else f"coherence={coherence:.3f} < {threshold:.3f} (domain={domain})"
            ),
        )