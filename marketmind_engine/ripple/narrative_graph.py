"""
Emergent Narrative Graph

Builds symbol co-mention clusters dynamically from RSS items.
"""

from collections import defaultdict
from typing import List, Dict


class NarrativeGraph:

    def build_symbol_counts(self, items: List) -> Dict[str, int]:
        """
        Extract and count symbol mentions from narrative items.
        Expects items with .title attribute.
        """

        import re
        ticker_pattern = re.compile(r"\b[A-Z]{2,5}\b")

        counts = defaultdict(int)

        for item in items:
            tokens = ticker_pattern.findall(item.title)
            for token in tokens:
                if token not in ["AI", "IPO", "FDA", "USA", "US", "NYSE", "WSJ", "CNBC"]:
                    counts[token] += 1

        return dict(counts)
