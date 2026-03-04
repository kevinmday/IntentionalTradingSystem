from typing import Dict, Any, List
from statistics import mean, pstdev
import time

from .relative_signal_layer import RelativeSignalLayer


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
        self.relative_layer = RelativeSignalLayer()

    # ==========================================================
    # PUBLIC ENTRY
    # ==========================================================

    def snapshot(self) -> Dict[str, Any]:

        try:
            structural = self._structural_layer()
            narrative = self._narrative_layer()
            capital = self._capital_layer()

            composite = self._composite(structural, narrative, capital)

            # FIX: match RelativeSignalLayer signature
            relative_signals = self.relative_layer.evaluate(
                structural,
                narrative,
                capital,
            )

            return {
                "mode": "propagation_live",
                "timestamp": time.time(),
                "structural": structural,
                "narrative": narrative,
                "capital": capital,
                "composite": composite,
                "relative_signals": relative_signals,
            }

        except Exception as e:
            return {
                "mode": "propagation_error",
                "timestamp": time.time(),
                "error": str(e),
            }

    # ==========================================================
    # HELPER
    # ==========================================================

    def _extract_change(self, record: Dict[str, Any]) -> float | None:

        if not isinstance(record, dict):
            return None

        if "percent_change" in record:
            return record["percent_change"]

        if "pct_change" in record:
            return record["pct_change"]

        return None

    # ==========================================================
    # STRUCTURAL LAYER
    # ==========================================================

    def _structural_layer(self) -> Dict[str, float]:

        data = {}

        if hasattr(self.provider, "get_batch_data"):
            try:
                data = self.provider.get_batch_data(STRUCTURAL_SYMBOLS)
            except Exception:
                data = {}

        if not data:
            return {"bias": 0.0, "volatility": 0.0, "dispersion": 0.0}

        changes = []

        for v in data.values():

            change = self._extract_change(v)

            if change is None:
                continue

            try:
                changes.append(float(change))
            except Exception:
                continue

        if not changes:
            return {"bias": 0.0, "volatility": 0.0, "dispersion": 0.0}

        return {
            "bias": mean(changes),
            "volatility": pstdev(changes) if len(changes) > 1 else 0.0,
            "dispersion": max(changes) - min(changes),
        }

    # ==========================================================
    # NARRATIVE LAYER
    # ==========================================================

    def _narrative_layer(self) -> Dict[str, float]:

        symbols: List[str] = []

        if hasattr(self.rss_service, "get_evaluated_symbols"):
            try:
                symbols = self.rss_service.get_evaluated_symbols()
            except Exception:
                symbols = []

        if not symbols:
            return {"bias": 0.0, "concentration": 0.0, "momentum": 0.0}

        data = {}

        if hasattr(self.provider, "get_batch_data"):
            try:
                data = self.provider.get_batch_data(symbols)
            except Exception:
                data = {}

        if not data:
            return {"bias": 0.0, "concentration": 0.0, "momentum": 0.0}

        changes = []

        for v in data.values():

            change = self._extract_change(v)

            if change is None:
                continue

            try:
                changes.append(float(change))
            except Exception:
                continue

        if not changes:
            return {"bias": 0.0, "concentration": 0.0, "momentum": 0.0}

        return {
            "bias": mean(changes),
            "concentration": pstdev(changes) if len(changes) > 1 else 0.0,
            "momentum": mean(abs(c) for c in changes),
        }

    # ==========================================================
    # CAPITAL LAYER
    # ==========================================================

    def _capital_layer(self) -> Dict[str, float]:

        positions = []

        if hasattr(self.engine_controller, "get_open_positions"):
            try:
                positions = self.engine_controller.get_open_positions()
            except Exception:
                positions = []

        if not positions:
            return {"exposure": 0.0, "unrealized_pct": 0.0, "alignment": 0.0}

        unrealized = []
        directions = []

        for p in positions:

            if not isinstance(p, dict):
                continue

            unrealized.append(p.get("unrealized_pct", 0.0))
            directions.append(p.get("direction", 0.0))

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
            abs(structural["volatility"])
            + abs(narrative["concentration"])
            + abs(capital["unrealized_pct"])
        )

        alignment_score = (
            structural["bias"]
            * narrative["bias"]
            * (1 if capital["exposure"] >= 0 else -1)
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