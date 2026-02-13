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

    def run_cycle(self):

        macro_inputs = self._collect_macro_inputs()
        risk_directive = self.systemic_monitor.evaluate(macro_inputs)

        # --------------------------------------------------
        # HARD INTERRUPT OR COMPOSITE SYSTEMIC
        # --------------------------------------------------

        if risk_directive.flatten_all:
            self._flatten_all_positions()
            self.state.regime_mode = SystemicMode.STANDBY

            return {
                "timestamp": time(),
                "regime": self.state.regime_mode.value,
                "flatten_triggered": True,
                "block_new_entries": True,
            }

        # --------------------------------------------------
        # STANDBY HYSTERESIS LOCK
        # --------------------------------------------------

        if self.state.regime_mode == SystemicMode.STANDBY:

            composite = self._composite_score(macro_inputs)

            # Remain locked until stress drops below STRESSED threshold
            if composite >= self.systemic_monitor.STRESSED_THRESHOLD:
                return {
                    "timestamp": time(),
                    "regime": SystemicMode.STANDBY.value,
                    "flatten_triggered": False,
                    "block_new_entries": True,
                }

            # Recovery condition met
            self.state.regime_mode = SystemicMode.NORMAL

            return {
                "timestamp": time(),
                "regime": self.state.regime_mode.value,
                "flatten_triggered": False,
                "block_new_entries": False,
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
        }
