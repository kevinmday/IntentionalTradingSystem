import re
import sqlite3
from typing import List


class SymbolResolver:
    """
    Resolves potential ticker symbols from text
    against canonical asset_universe.db
    """

    def __init__(self, db_path: str = "asset_universe.db"):
        self.db_path = db_path
        self._load_symbols()

    def _load_symbols(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT symbol FROM assets")
        rows = cursor.fetchall()
        conn.close()

        self.symbol_set = {row[0] for row in rows}

    def extract_candidates(self, text: str) -> List[str]:
        """
        Extract possible ticker-like tokens from text.
        Rules:
        - 1–5 uppercase letters
        - Must be standalone tokens
        """

        tokens = re.findall(r"\b[A-Z]{1,5}\b", text)
        return tokens

    def resolve(self, text: str) -> List[str]:
        """
        Return validated tradable symbols found in text.
        """

        candidates = self.extract_candidates(text)

        resolved = [
            token for token in candidates
            if token in self.symbol_set
        ]

        # Remove duplicates while preserving order
        seen = set()
        ordered = []
        for symbol in resolved:
            if symbol not in seen:
                ordered.append(symbol)
                seen.add(symbol)

        return ordered