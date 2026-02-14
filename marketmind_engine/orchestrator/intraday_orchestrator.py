from dataclasses import dataclass
from time import time

from marketmind_engine.regime.systemic_monitor import (
    SystemicMonitor,
    SystemicInputs,
)
from marketmind_engine.regime.systemic_mode import SystemicMode


@dataclass
class OrchestratorState:
    regime_mode: SystemicMode = SystemicMode.NORMAL


class IntradayOrchestrator:
    """
    Intraday authority router.

    Phase 10:
    - Hard interrupt path (via monitor)
    - Composite regime path
    - SYSTEMIC flatten override
    - STANDBY hysteresis lock

    Phase 11.4:
    - Adds structured diagnostics transparency
    """

    def __init__(self, portfolio=None, execution_engine=None):
        self.systemic_monitor = SystemicMonitor()
        self.state = OrchestratorState()

        self.portfolio = portfolio
        self.execution_engine = execution_engine

    def _collect_macro_inputs(self) -> SystemicInputs:
        """
        Neutral baseline inputs.
        Replace with real telemetry wiring later.
        """

        return SystemicInputs(
            drawdown_velocity=0.0,
            liquidity_stress=0.0,
            correlation_spike=0.0,
            narrative_shock=0.0,
            structural_confirmation=0.0,
        )

    def _flatten_all_positions(self):
        """
        SYSTEMIC override.
        Close all open positions immediately.
        """

        if not self.portfolio or not self.execution_engine:
            return

        open_positions = self.portfolio.open_positions()

        for position in open_positions:
            self.execution_engine.close(position)

    def _composite_score(self, inputs: SystemicInputs) -> float:
        return (
            inputs.drawdown_velocity
            + inputs.liquidity_stress
            + inputs.correlation_spike
            + inputs.narrative_shock
            + inputs.structural_confirmation
        ) / 5.0

    # ------------------------------------------------------------------
    # PHASE 11.4 — RUN CYCLE WITH DIAGNOSTICS
    # ------------------------------------------------------------------

    def run_cycle(self):

        macro_inputs = self._collect_macro_inputs()
        risk_directive = self.systemic_monitor.evaluate(macro_inputs)

        composite = self._composite_score(macro_inputs)

        diagnostics = {
            "macro_inputs": {
                "drawdown_velocity": macro_inputs.drawdown_velocity,
                "liquidity_stress": macro_inputs.liquidity_stress,
                "correlation_spike": macro_inputs.correlation_spike,
                "narrative_shock": macro_inputs.narrative_shock,
                "structural_confirmation": macro_inputs.structural_confirmation,
            },
            "composite_score": composite,
            "stressed_threshold": self.systemic_monitor.STRESSED_THRESHOLD,
            "risk_mode": risk_directive.mode.value,
            "flatten_all": risk_directive.flatten_all,
            "block_new_entries": risk_directive.block_new_entries,
        }

        # --------------------------------------------------
        # HARD INTERRUPT
        # --------------------------------------------------

        if risk_directive.flatten_all:
            self._flatten_all_positions()
            self.state.regime_mode = SystemicMode.STANDBY

            return {
                "timestamp": time(),
                "regime": self.state.regime_mode.value,
                "flatten_triggered": True,
                "block_new_entries": True,
                "diagnostics": diagnostics,
            }

        # --------------------------------------------------
        # STANDBY HYSTERESIS LOCK
        # --------------------------------------------------

        if self.state.regime_mode == SystemicMode.STANDBY:

            if composite >= self.systemic_monitor.STRESSED_THRESHOLD:
                return {
                    "timestamp": time(),
                    "regime": SystemicMode.STANDBY.value,
                    "flatten_triggered": False,
                    "block_new_entries": True,
                    "diagnostics": diagnostics,
                }

            # Recovery condition
            self.state.regime_mode = SystemicMode.NORMAL

            return {
                "timestamp": time(),
                "regime": self.state.regime_mode.value,
                "flatten_triggered": False,
                "block_new_entries": False,
                "diagnostics": diagnostics,
            }

        # --------------------------------------------------
        # NORMAL / STRESSED / PRE_SYSTEMIC FLOW
        # --------------------------------------------------

        self.state.regime_mode = risk_directive.mode

        return {
            "timestamp": time(),
            "regime": self.state.regime_mode.value,
            "flatten_triggered": False,
            "block_new_entries": risk_directive.block_new_entries,
            "diagnostics": diagnostics,
        }
