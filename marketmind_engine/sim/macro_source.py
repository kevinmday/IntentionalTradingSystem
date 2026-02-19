from typing import List, Dict, Any, Optional


class SyntheticMacroSource:
    """
    Deterministic macro regime injector.

    Schedule example:
        [
            {"ts": 0, "macro_regime": "risk_on"},
            {"ts": 5, "macro_regime": "risk_off"},
        ]

    Only emits when clock.now() matches an entry.
    """

    def __init__(self, schedule: List[Dict[str, Any]], clock):
        self._schedule = {entry["ts"]: entry for entry in schedule}
        self._clock = clock

    def collect(self) -> Optional[Dict[str, Any]]:
        ts = self._clock.now()
        return self._schedule.get(ts)
