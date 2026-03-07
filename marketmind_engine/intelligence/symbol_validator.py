from typing import Set

import yfinance as yf


class SymbolValidator:
    """
    Maintains a universe of tradable symbols and validates candidates.
    Cached in memory so the engine loop stays fast.
    """

    def __init__(self):

        self.valid_symbols: Set[str] = set()

        self._build_universe()

    def _build_universe(self):

        # Core high-liquidity universe (fast + reliable)
        seed = [
            "SPY", "QQQ", "DIA", "IWM",
            "NVDA", "AMD", "TSLA", "AAPL", "MSFT",
            "META", "AMZN", "GOOGL",
            "LMT", "RTX", "NOC",
            "LLY", "ILMN",
            "ROKU", "PINS",
            "RKLB"
        ]

        for s in seed:
            self.valid_symbols.add(s)

        # Attempt to extend with Yahoo data (optional)
        try:

            tickers = yf.Tickers("SPY QQQ NVDA AMD TSLA")

            for t in tickers.tickers.keys():
                self.valid_symbols.add(t.upper())

        except Exception:
            pass

    def is_valid(self, symbol: str) -> bool:

        if not symbol:
            return False

        symbol = symbol.upper()

        # Basic sanity rules
        if len(symbol) > 5:
            return False

        if not symbol.isalpha():
            return False

        if self.valid_symbols and symbol not in self.valid_symbols:
            return False

        return True