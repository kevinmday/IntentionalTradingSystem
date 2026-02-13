from dataclasses import dataclass
from marketmind_engine.regime.systemic_mode import SystemicMode

@dataclass(frozen=True)
class RegimeSnapshot:
    timestamp: float
    regime: SystemicMode
    fils: float = 0.0
    ttcf: float = 0.0
    drift: float = 0.0
    sector_stress: float = 0.0
    narrative_density: float = 0.0
    cross_domain_convergence: float = 0.0
    drawdown_velocity: float = 0.0
