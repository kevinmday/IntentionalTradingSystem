"""
DataProvider Interface
----------------------
Data interface contract for the MarketMind engine.

All data sources (stub, live, replay, RSS, MoltBook, etc.)
must implement this interface.

The engine consumes *normalized numbers*, not feeds,
streams, APIs, or files.
"""

from typing import Protocol, Dict, Any, List, Optional


class DataProvider(Protocol):
    """
    Contract for all engine data providers.
    """

    # Human-readable identifier (e.g. "stub", "alpaca", "replay")
    name: str

    def get_symbol_data(
        self,
        symbol: str,
        context: Optional[dict] = None,
    ) -> Dict[str, Any]:
        """
        Return normalized numeric data required for analysis
        of a single symbol.

        MUST return numbers only (no timestamps, no clocks).
        """
        ...

    def get_batch_data(
        self,
        symbols: List[str],
        context: Optional[dict] = None,
    ) -> Dict[str, Dict[str, Any]]:
        """
        Return normalized numeric data for multiple symbols.

        Keys must be uppercase symbol strings.
        """
        ...

    def metadata(self) -> Dict[str, Any]:
        """
        Describe the provider.

        Used for provenance, debugging, replay,
        and post-trade audit.
        """
        ...
