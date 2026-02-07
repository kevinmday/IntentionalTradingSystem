from dataclasses import dataclass
from datetime import datetime
from typing import Optional
import json


# ============================================================
# Ignition Observation Record
# ============================================================

@dataclass(frozen=True)
class IgnitionObservation:
    """
    Immutable snapshot of ignition + liquidity state
    at a single decision moment.

    This is observational only.
    It must NEVER influence execution.
    """

    # identity
    timestamp: datetime
    symbol: str

    # time context
    is_open_window: bool
    seconds_from_open: Optional[int]

    # liquidity state
    volume_ratio: float
    trade_ratio: Optional[float]
    volume_median: float
    trade_median: Optional[float]

    # ignition
    ignition_delta: Optional[float]
    ignition_used: bool

    # proximity flags
    near_volume: bool
    near_trade: bool

    # thresholds (embedded for replay safety)
    volume_threshold: float
    trade_threshold: float
    relax_volume_threshold: float
    relax_trade_threshold: float


# ============================================================
# Observer Interface
# ============================================================

class IgnitionObserver:
    """
    Observer interface for recording ignition observations.

    Implementations must:
    - be side-effect safe
    - never raise into caller
    - never influence decisions
    """

    def record(self, obs: IgnitionObservation) -> None:
        raise NotImplementedError


# ============================================================
# Null Observer (Default / Safe)
# ============================================================

class NullIgnitionObserver(IgnitionObserver):
    """
    Default no-op observer.

    Guarantees zero behavioral impact when no observer
    is explicitly attached.
    """

    def record(self, obs: IgnitionObservation) -> None:
        return


# ============================================================
# File-backed Observer (JSONL)
# ============================================================

class FileIgnitionObserver(IgnitionObserver):
    """
    Appends ignition observations to a JSONL file.

    - One record per line
    - Append-only
    - Crash-safe
    - Analysis-friendly
    """

    def __init__(self, path: str):
        self.path = path

    def record(self, obs: IgnitionObservation) -> None:
        try:
            with open(self.path, "a", encoding="utf-8") as f:
                f.write(json.dumps(obs.__dict__, default=str))
                f.write("\n")
        except Exception:
            # Observation must NEVER interfere with execution
            return