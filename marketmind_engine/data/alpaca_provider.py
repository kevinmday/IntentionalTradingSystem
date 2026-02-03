# marketmind_engine/data/alpaca_provider.py

from typing import Dict


class AlpacaProvider:
    """
    Skeleton Alpaca data provider.

    This class defines the interface and intent for Alpaca-backed
    market data access, but does NOT perform any API calls.

    Purpose:
    - Contract validation
    - Provider wiring
    - UX / adapter integration
    - Capability declaration

    Live data access is intentionally unimplemented.
    """

    name = "alpaca"
    mode = "live"

    # Declared (not enforced) capabilities
    capabilities = {
        "quotes": True,
        "bars": True,
        "volume": True,
        "historical": True,
        "orders": False,   # engine must never place orders
        "streaming": False
    }

    def __init__(self, config: Dict | None = None):
        """
        config is accepted for future compatibility,
        but unused in the skeleton implementation.
        """
        self.config = config or {}

    def get_symbol_data(self, symbol: str) -> Dict:
        """
        Skeleton method.

        This provider intentionally does NOT return live data.
        Any attempt to call this before implementation is a hard error.
        """
        raise NotImplementedError(
            "AlpacaProvider is a skeleton only. "
            "Live market data access is not yet implemented."
        )
