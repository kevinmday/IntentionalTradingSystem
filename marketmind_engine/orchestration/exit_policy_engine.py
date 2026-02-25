from dataclasses import dataclass


@dataclass(frozen=True)
class ExitTriggerEvent:
    symbol: str
    trigger_type: str
    engine_time: int

    price: float
    entry_price: float
    peak_price: float

    drift: float
    ttcf: float
    delta_since_ignition: float

    monitoring_tier: int