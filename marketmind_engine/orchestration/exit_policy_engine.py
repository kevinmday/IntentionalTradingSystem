from dataclasses import dataclass
from typing import Dict


# ----------------------------------------
# ExitTriggerEvent
# ----------------------------------------

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


# ----------------------------------------
# PortfolioState
# ----------------------------------------

@dataclass(frozen=True)
class PortfolioState:
    total_capital: float
    open_positions: Dict[str, float]
    total_unrealized_pnl: float
    systemic_risk_level: float


# ----------------------------------------
# ExitDirective
# ----------------------------------------

@dataclass(frozen=True)
class ExitDirective:
    symbol: str
    action: str
    size_fraction: float
    reason: str


# ----------------------------------------
# ExitPolicyEngine
# ----------------------------------------

class ExitPolicyEngine:

    def __init__(self, systemic_risk_override: float = 0.75):
        self.systemic_risk_override = systemic_risk_override

    def evaluate(self, trigger: ExitTriggerEvent, portfolio_state: PortfolioState) -> ExitDirective:

        # Systemic override
        if portfolio_state.systemic_risk_level >= self.systemic_risk_override:
            return ExitDirective(
                symbol=trigger.symbol,
                action="FULL_EXIT",
                size_fraction=1.0,
                reason="SYSTEMIC_RISK_OVERRIDE",
            )

        if trigger.trigger_type == "HARD_STOP":
            return ExitDirective(
                symbol=trigger.symbol,
                action="FULL_EXIT",
                size_fraction=1.0,
                reason="HARD_STOP",
            )

        if trigger.trigger_type == "CHAOS_ESCALATION":
            return ExitDirective(
                symbol=trigger.symbol,
                action="FULL_EXIT",
                size_fraction=1.0,
                reason="CHAOS_ESCALATION",
            )

        if trigger.trigger_type == "DRIFT_COLLAPSE":
            return ExitDirective(
                symbol=trigger.symbol,
                action="FULL_EXIT",
                size_fraction=1.0,
                reason="DRIFT_COLLAPSE",
            )

        if trigger.trigger_type == "PEAK_GIVEBACK":
            return ExitDirective(
                symbol=trigger.symbol,
                action="PARTIAL_EXIT",
                size_fraction=0.5,
                reason="PEAK_GIVEBACK",
            )

        return ExitDirective(
            symbol=trigger.symbol,
            action="IGNORE",
            size_fraction=0.0,
            reason="NO_POLICY_MATCH",
        )