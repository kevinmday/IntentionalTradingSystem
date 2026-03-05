"""
MarketMind Research Question Evaluator

Consumes PropagationEngine snapshot
and produces deterministic likelihood + traceback.
"""

from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class ResearchResult:
    question: str
    domain: str
    likelihood: float
    drivers: Dict[str, float]
    snapshot: Dict[str, Any]


class QuestionEvaluator:

    def evaluate(
        self,
        question: str,
        domain: str,
        snapshot: Dict[str, Any],
    ) -> ResearchResult:

        narrative = snapshot.get("narrative", {})
        structural = snapshot.get("structural", {})
        capital = snapshot.get("capital", {})

        narrative_momentum = float(narrative.get("momentum", 0.0))
        narrative_concentration = float(narrative.get("concentration", 0.0))

        structural_volatility = float(structural.get("volatility", 0.0))
        structural_dispersion = float(structural.get("dispersion", 0.0))

        capital_alignment = abs(float(capital.get("alignment", 0.0)))

        drivers = {
            "narrative_momentum": narrative_momentum,
            "narrative_concentration": narrative_concentration,
            "structural_volatility": structural_volatility,
            "structural_dispersion": structural_dispersion,
            "capital_alignment": capital_alignment,
        }

        likelihood = (
            0.35 * narrative_momentum
            + 0.25 * narrative_concentration
            + 0.20 * structural_volatility
            + 0.10 * structural_dispersion
            + 0.10 * capital_alignment
        )

        likelihood = max(0.0, min(1.0, likelihood))

        return ResearchResult(
            question=question,
            domain=domain,
            likelihood=likelihood,
            drivers=drivers,
            snapshot=snapshot,
        )