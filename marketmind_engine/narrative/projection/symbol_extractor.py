import re
from typing import List


class SymbolExtractor:
    """
    Deterministic literal ticker extractor (v1).

    Extracts:
    - $TICKER
    - Standalone uppercase tokens (2–5 chars)

    Does NOT:
    - Infer implied tickers
    - Perform NLP
    - Use probabilistic scoring
    """

    # Matches $NVDA
    DOLLAR_PATTERN = re.compile(r"\$([A-Z]{1,5})")

    # Matches standalone NVDA (not part of larger word)
    STANDALONE_PATTERN = re.compile(r"\b([A-Z]{2,5})\b")

    def extract(self, text: str) -> List[str]:
        if not text:
            return []

        symbols = set()

        # $TICKER matches
        for match in self.DOLLAR_PATTERN.findall(text):
            symbols.add(match)

        # Standalone uppercase matches
        for match in self.STANDALONE_PATTERN.findall(text):
            symbols.add(match)

        return sorted(symbols)