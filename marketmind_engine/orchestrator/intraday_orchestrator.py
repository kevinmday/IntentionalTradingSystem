from dataclasses import dataclass
from time import time

from marketmind_engine.regime.systemic_monitor import (
    SystemicMonitor,
    SystemicInputs,
)
from marketmind_engine.regime.systemic_mode import SystemicMode

from marketmind_engine.regime.macro_sources.base import MacroInputSource

from marketmind_engine.execution.policy.default_policy import (
    DefaultRegimeExecutionPolicy,
)
from marketmind_engine.execution.policy.base import ExecutionDirective


@dataclass
class OrchestratorState:
    regime_mode: SystemicMode = SystemicMode.NORMAL


class IntradayOrchestrator:
    """
    Intraday authority router.

    Phase 10:
    - Hard interrupt path
    - Composite regime path
    - SYSTEMIC flatten override
    - STANDBY hysteresis lock

    Phase 11.5:
    - Pluggable MacroInputSource

    Phase 12A:
    - Persistent regime transition audit logging

    Phase 12:
    - Regime-driven execution gating
    """

    def __init__(
        self,
        macro_source: MacroInputSource,
        portfolio=None,
        execution_engine=None,
        audit_writer=None,
        execution_policy=None,
    ):
        self._macro_source = macro_source
        self._audit_writer = audit_writer

        self.systemic_monitor = SystemicMonitor()
        self.state = OrchestratorState()

        self.portfolio = portfolio
        self.execution_engine = execution_engine

        self._execution_policy = (
            execution_policy or DefaultRegimeExecutionPolicy()
        )

    # ------------------------------------------------------------------
    # INTERNAL LIVE COLLECTOR
    # ------------------------------------------------------------------

    def _collect_macro_inputs(self) -> SystemicInputs:
        return SystemicInputs(
            drawdown_velocity=0.0,
            liquidity_stress=0.0,
            correlation_spike=0.0,
            narrative_shock=0.0,
            structural_confirmation=0.0,
        )

    # ------------------------------------------------------------------
    # SYSTEMIC FLATTEN
    # ------------------------------------------------------------------

    def _flatten_all_positions(self):

        if not self.portfolio or not self.execution_engine:
            return

        open_positions = self.portfolio.open_positions()

        for position in open_positions:
            self.execution_engine.close(position)

    # ------------------------------------------------------------------
    # COMPOSITE SCORE
    # ------------------------------------------------------------------

    def _composite_score(self, inputs: SystemicInputs) -> float:
        return (
            inputs.drawdown_velocity
            + inputs.liquidity_stress
            + inputs.correlation_spike
            + inputs.narrative_shock
            + inputs.structural_confirmation
        ) / 5.0

    # ------------------------------------------------------------------
    # AUDIT TRANSITION HOOK
    # ------------------------------------------------------------------

    def _audit_transition(
        self,
        previous_mode: SystemicMode,
        new_mode: SystemicMode,
        composite: float,
        flatten_all: bool,
        block_new_entries: bool,
    ):

        if not self._audit_writer:
            return

        from marketmind_engine.regime.audit.schema import RegimeTransitionEvent

        event = RegimeTransitionEvent(
            timestamp=time(),
            previous_regime=previous_mode.value,
            new_regime=new_mode.value,
            composite_score=composite,
            hard_interrupt=flatten_all,
            block_new_entries=block_new_entries,
            hysteresis_locked=(previous_mode == SystemicMode.STANDBY),
            macro_source_type=self._macro_source.source_type,
            injected_mode=(self._macro_source.source_type != "live"),
        )

        self._audit_writer.write(event)

    # ------------------------------------------------------------------
    # RUN CYCLE
    # ------------------------------------------------------------------

    def run_cycle(self):

        macro_inputs = self._macro_source.collect()

        risk_directive = self.systemic_monitor.evaluate(macro_inputs)

        composite = self._composite_score(macro_inputs)

        diagnostics = {
            "macro_source_type": self._macro_source.source_type,
            "macro_inputs": {
                "drawdown_velocity": macro_inputs.drawdown_velocity,
                "liquidity_stress": macro_inputs.liquidity_stress,
                "correlation_spike": macro_inputs.correlation_spike,
                "narrative_shock": macro_inputs.narrative_shock,
                "structural_confirmation": macro_inputs.structural_confirmation,
            },
            "composite_score": composite,
            "risk_mode": risk_directive.mode.value,
            "flatten_all": risk_directive.flatten_all,
            "block_new_entries": risk_directive.block_new_entries,
        }

        previous_mode = self.state.regime_mode

        # --------------------------------------------------
        # HARD INTERRUPT
        # --------------------------------------------------

        if risk_directive.flatten_all:

            if previous_mode != SystemicMode.STANDBY:
                self._audit_transition(
                    previous_mode,
                    SystemicMode.STANDBY,
                    composite,
                    flatten_all=True,
                    block_new_entries=True,
                )

            self._flatten_all_positions()
            self.state.regime_mode = SystemicMode.STANDBY

        # --------------------------------------------------
        # STANDBY LOCK
        # --------------------------------------------------

        elif previous_mode == SystemicMode.STANDBY:

            if composite < self.systemic_monitor.STRESSED_THRESHOLD:

                self._audit_transition(
                    previous_mode,
                    SystemicMode.NORMAL,
                    composite,
                    flatten_all=False,
                    block_new_entries=False,
                )

                self.state.regime_mode = SystemicMode.NORMAL

        # --------------------------------------------------
        # NORMAL FLOW
        # --------------------------------------------------

        else:

            if previous_mode != risk_directive.mode:
                self._audit_transition(
                    previous_mode,
                    risk_directive.mode,
                    composite,
                    flatten_all=False,
                    block_new_entries=risk_directive.block_new_entries,
                )

            self.state.regime_mode = risk_directive.mode

        # --------------------------------------------------
        # EXECUTION DIRECTIVE (Phase 12)
        # --------------------------------------------------

        execution_directive: ExecutionDirective = (
            self._execution_policy.resolve(self.state.regime_mode)
        )

        return {
            "timestamp": time(),
            "regime": self.state.regime_mode.value,
            "flatten_triggered": risk_directive.flatten_all,
            "block_new_entries": execution_directive.allow_entries is False,
            "execution": {
                "allow_entries": execution_directive.allow_entries,
                "size_multiplier": execution_directive.size_multiplier,
                "risk_level": execution_directive.risk_level,
            },
            "diagnostics": diagnostics,
        }
