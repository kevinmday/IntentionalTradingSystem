from dataclasses import dataclass
from .systemic_mode import SystemicMode


@dataclass(frozen=True)
class RiskDirective:
    """
    Deterministic regime-derived execution authority.
    No engine logic.
    No mutation.
    """

    mode: SystemicMode

    # Hard controls
    flatten_all: bool = False
    block_new_entries: bool = False

    # Continuous sizing authority (Phase-12C)
    size_multiplier: float = 1.0

    # Optional operational flags
    increase_telemetry: bool = False

    # Audit rationale
    reason: str = ""
