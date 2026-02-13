from dataclasses import dataclass
from .systemic_mode import SystemicMode

@dataclass(frozen=True)
class RiskDirective:
    mode: SystemicMode
    flatten_all: bool = False
    block_new_entries: bool = False
    increase_telemetry: bool = False
    reason: str = ""
