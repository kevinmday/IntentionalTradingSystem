"""
Stub Data Provider
------------------
Deterministic placeholder provider used until
live market, narrative, and broker feeds are wired.

This provider MUST:
- Return numeric values only
- Be deterministic
- Contain no clocks, timestamps, or engine state
"""

from typing import Dict, Any, List, Optional
import os

from marketmind_engine.data.interface import DataProvider


class StubDataProvider(DataProvider):
    """
    Stub implementation of DataProvider.
    """

    name: str = "stub"

    def get_symbol_data(
        self,
        symbol: str,
        context: Optional[dict] = None,
    ) -> Dict[str, Any]:
        """
        Return normalized numeric data for a single symbol.
        """

        stub_mode = os.getenv("MARKETMIND_STUB_MODE", "passive").lower()

        # -----------------------------
        # ACTIVE MODE (tradeable stub)
        # -----------------------------
        if stub_mode == "active":
            return {
                # Core intention / signal placeholders
                "signal": 1.0,
                "fils": 0.88,
                "ucip": 0.71,
                "ttcf": 0.05,
                "confidence": 0.91,

                # Tradeable fields expected downstream
                "eligible": True,
                "score": 82,
                "price": 100.0,
                "recommended_quantity": 5,
                "regime": "neutral",
            }

        # -----------------------------
        # PASSIVE MODE (default)
        # -----------------------------
        return {
            # Core intention / signal placeholders
            "signal": 0.0,
            "fils": 0.61,
            "ucip": 0.44,
            "ttcf": 0.18,
            "confidence": 0.72,
        }

    def get_batch_data(
        self,
        symbols: List[str],
        context: Optional[dict] = None,
    ) -> Dict[str, Dict[str, Any]]:
        """
        Return normalized numeric data for multiple symbols.
        """
        return {
            s.upper(): self.get_symbol_data(s, context)
            for s in symbols
        }

    def metadata(self) -> Dict[str, Any]:
        """
        Provider metadata for provenance and audit.
        """
        return {
            "provider": self.name,
            "mode": os.getenv("MARKETMIND_STUB_MODE", "passive"),
            "live": False,
        }