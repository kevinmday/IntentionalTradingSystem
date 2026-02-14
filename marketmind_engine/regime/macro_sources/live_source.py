from typing import Dict
from .base import MacroInputSource


class LiveMacroSource:
    """
    Production macro source.
    Delegates to orchestrator collector.
    """

    def __init__(self, collector_callable):
        self._collector = collector_callable

    def collect(self) -> Dict:
        return self._collector()

    @property
    def source_type(self) -> str:
        return "live"
