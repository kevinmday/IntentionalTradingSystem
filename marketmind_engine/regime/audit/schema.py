from dataclasses import dataclass, asdict


@dataclass(frozen=True)
class RegimeTransitionEvent:
    timestamp: float
    previous_regime: str
    new_regime: str
    composite_score: float
    hard_interrupt: bool
    block_new_entries: bool
    hysteresis_locked: bool
    macro_source_type: str
    injected_mode: bool

    def to_dict(self) -> dict:
        return asdict(self)
