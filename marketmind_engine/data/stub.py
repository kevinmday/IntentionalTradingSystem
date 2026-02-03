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
        return {
            # Core intention / signal placeholders
            "signal": 0.0,          # numeric placeholder (e.g. HOLD)
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
            "mode": "stub",
            "live": False,
        }
