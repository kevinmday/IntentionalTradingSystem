"""
Phase-9B: Decision-level persistence.

Purpose:
- Persist and reload DecisionResult
- No engine logic
- No Bell-Drake awareness
- No invented symbols
"""

import pickle
from pathlib import Path
from typing import Optional

from marketmind_engine.decision.types import DecisionResult


class PersistentDecisionEvaluator:
    """
    Minimal persistence adapter for DecisionResult.
    """

    def __init__(self, storage_path: Path):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self._file = self.storage_path / "latest_decision.pkl"

    def persist(self, decision: DecisionResult) -> None:
        """
        Persist the latest DecisionResult.
        """
        with open(self._file, "wb") as f:
            pickle.dump(decision, f)

    def load_latest(self) -> Optional[DecisionResult]:
        """
        Load the most recently persisted DecisionResult.
        Returns None if nothing has been persisted yet.
        """
        if not self._file.exists():
            return None

        with open(self._file, "rb") as f:
            return pickle.load(f)