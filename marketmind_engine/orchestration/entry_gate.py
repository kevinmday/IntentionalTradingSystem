from dataclasses import dataclass
from typing import List
from marketmind_engine.state.contracts import MarketState


@dataclass
class EntryDecision:
    allow: bool
    reasons: List[str]


class EntryGate:
    """
    Quant confirmation gate for intraday entry.
    Pure evaluation layer.
    """

    def __init__(
        self,
        min_delta: float = 0.002,        # 0.2% move
        min_volume_ratio: float = 1.2,
        max_ttcf: float = 0.18,
        min_drift: float = 0.015,
        max_latency_seconds: int = 600,
    ):
        self.min_delta = min_delta
        self.min_volume_ratio = min_volume_ratio
        self.max_ttcf = max_ttcf
        self.min_drift = min_drift
        self.max_latency_seconds = max_latency_seconds

    def evaluate(self, state: MarketState) -> EntryDecision:
        reasons = []

        # --- Latency Guard ---
        if state.ignition_time is None:
            reasons.append("NO_IGNITION")
        else:
            latency = state.engine_time - state.ignition_time
            if latency > self.max_latency_seconds:
                reasons.append(f"LATENCY_TOO_HIGH ({latency}s)")

        # --- Price Displacement Guard ---
        delta = getattr(state, "delta_since_ignition", state.price_delta)
        if delta is None or delta < self.min_delta:
            reasons.append(f"DELTA_TOO_LOW ({delta})")

        # --- Volume Guard ---
        if state.volume_ratio < self.min_volume_ratio:
            reasons.append(f"VOLUME_TOO_LOW ({state.volume_ratio})")

        # --- Chaos Guard ---
        if state.ttcf > self.max_ttcf:
            reasons.append(f"TTCF_TOO_HIGH ({state.ttcf})")

        # --- Drift Guard ---
        drift = getattr(state, "drift", 0.0)
        if drift < self.min_drift:
            reasons.append(f"DRIFT_TOO_LOW ({drift})")

        allow = len(reasons) == 0

        return EntryDecision(allow=allow, reasons=reasons)
