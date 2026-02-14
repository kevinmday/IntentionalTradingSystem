from typing import Dict, List
from .base import MacroInputSource


class ReplayMacroSource:
    """
    Deterministic replay provider.
    Advances per collect() call.
    """

    def __init__(self, frames: List[Dict]):
        if not frames:
            raise ValueError("ReplayMacroSource requires non-empty frame list")

        self._frames = frames
        self._index = 0

    def collect(self) -> Dict:
        if self._index >= len(self._frames):
            return self._frames[-1]

        frame = self._frames[self._index]
        self._index += 1
        return frame

    @property
    def source_type(self) -> str:
        return "replay"
