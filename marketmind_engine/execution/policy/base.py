from dataclasses import dataclass
from marketmind_engine.regime.systemic_mode import SystemicMode


@dataclass(frozen=True)
class ExecutionDirective:
    allow_entries: bool
    size_multiplier: float
    risk_level: str


class RegimeExecutionPolicy:
    def resolve(self, regime: SystemicMode) -> ExecutionDirective:
        raise NotImplementedError
