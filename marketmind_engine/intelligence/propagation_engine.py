from typing import Dict, Any, List
from statistics import mean, pstdev
import time


STRUCTURAL_SYMBOLS = [
    "SPY",
    "QQQ",
    "DIA",
    "IWM",
    "XLF",
    "XLE",
    "XLV",
    "SMH",
    "ITA",
]


class PropagationEngine:
    """
    Stateless multi-layer propagation aggregator.

    Pure read-only intelligence layer.
    No mutation.
    No execution influence.
    No lifecycle interaction.
    """

    def __init__(self, provider, engine_controller, rss_service):
        self.provider = provider
        self.engine_controller = engine_controller
        self.rss_service = rss_service

    # ==========================================================
    # PUBLIC ENTRY
    # ==========================================================

    def snapshot(self) -> Dict[str, Any]:
        structural = self._structural_layer()
        narrative = self._narrative_layer()
        capital = self._capital_layer()

        composite = self._composite(structural, narrative, capital)

        return {
            "mode": "propagation_live",
            "timestamp": time.time(),
            "structural": structural,
            "narrative": narrative,
            "capital": capital,
            "composite": composite,
        }

    # ==========================================================
    # LAYER 1 — STRUCTURAL
    # ==========================================================

    def _structural_layer(self) -> Dict[str, float]:
        data = self.provider.get_batch_snapshot(STRUCTURAL_SYMBOLS)

        if not data:
            return {"bias": 0.0, "volatility": 0.0, "dispersion": 0.0}

        changes = [v["pct_change"] for v in data.values() if "pct_change" in v]

        if not changes:
            return {"bias": 0.0, "volatility": 0.0, "dispersion": 0.0}

        return {
            "bias": mean(changes),
            "volatility": pstdev(changes) if len(changes) > 1 else 0.0,
            "dispersion": max(changes) - min(changes),
        }

    # ==========================================================
    # LAYER 2 — NARRATIVE
    # ==========================================================

    def _narrative_layer(self) -> Dict[str, float]:
        symbols: List[str] = self.rss_service.get_evaluated_symbols()

        if not symbols:
            return {"bias": 0.0, "concentration": 0.0, "momentum": 0.0}

        data = self.provider.get_batch_snapshot(symbols)

        if not data:
            return {"bias": 0.0, "concentration": 0.0, "momentum": 0.0}

        changes = [v["pct_change"] for v in data.values() if "pct_change" in v]

        if not changes:
            return {"bias": 0.0, "concentration": 0.0, "momentum": 0.0}

        return {
            "bias": mean(changes),
            "concentration": pstdev(changes) if len(changes) > 1 else 0.0,
            "momentum": mean(abs(c) for c in changes),
        }

    # ==========================================================
    # LAYER 3 — CAPITAL
    # ==========================================================

    def _capital_layer(self) -> Dict[str, float]:
        positions = self.engine_controller.get_open_positions()

        if not positions:
            return {"exposure": 0.0, "unrealized_pct": 0.0, "alignment": 0.0}

        unrealized = [p.get("unrealized_pct", 0.0) for p in positions]
        directions = [p.get("direction", 0.0) for p in positions]

        exposure = mean(directions) if directions else 0.0
        unrealized_avg = mean(unrealized) if unrealized else 0.0

        return {
            "exposure": exposure,
            "unrealized_pct": unrealized_avg,
            "alignment": exposure * unrealized_avg,
        }

    # ==========================================================
    # COMPOSITE
    # ==========================================================

    def _composite(self, structural, narrative, capital) -> Dict[str, Any]:
        stress_score = (
            abs(structural["volatility"]) +
            abs(narrative["concentration"]) +
            abs(capital["unrealized_pct"])
        )

        alignment_score = (
            structural["bias"] *
            narrative["bias"] *
            (1 if capital["exposure"] >= 0 else -1)
        )

        regime_hint = "neutral"
        if stress_score > 2:
            regime_hint = "elevated"
        if stress_score > 4:
            regime_hint = "unstable"

        return {
            "stress_score": round(stress_score, 4),
            "alignment_score": round(alignment_score, 4),
            "regime_hint": regime_hint,
        }