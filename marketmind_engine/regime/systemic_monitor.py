from dataclasses import dataclass
from .systemic_mode import SystemicMode
from .risk_directive import RiskDirective


@dataclass
class SystemicInputs:
    drawdown_velocity: float
    liquidity_stress: float
    correlation_spike: float
    narrative_shock: float
    structural_confirmation: float


class SystemicMonitor:
    """
    Two-path macro classifier:

    1) Hard interrupt path (discontinuity detection)
    2) Composite regime path (continuous stress escalation)

    Stateless and deterministic.
    """

    # -----------------------------
    # Hard Interrupt Thresholds
    # -----------------------------

    HARD_DRAWDOWN_THRESHOLD = 0.95
    HARD_CORRELATION_THRESHOLD = 0.97
    HARD_LIQUIDITY_THRESHOLD = 0.98

    # -----------------------------
    # Composite Regime Thresholds
    # -----------------------------

    SYSTEMIC_THRESHOLD = 0.85
    PRE_SYSTEMIC_THRESHOLD = 0.70
    STRESSED_THRESHOLD = 0.55

    # ----------------------------------------------------------
    # Hard Interrupt Path
    # ----------------------------------------------------------

    def _hard_interrupt(self, inputs: SystemicInputs) -> bool:
        """
        Detect structural rupture.
        Immediate SYSTEMIC if triggered.
        No averaging.
        No hysteresis.
        """

        if inputs.drawdown_velocity >= self.HARD_DRAWDOWN_THRESHOLD:
            return True

        if inputs.correlation_spike >= self.HARD_CORRELATION_THRESHOLD:
            return True

        if inputs.liquidity_stress >= self.HARD_LIQUIDITY_THRESHOLD:
            return True

        return False

    # ----------------------------------------------------------
    # Evaluation Entry Point
    # ----------------------------------------------------------

    def evaluate(self, inputs: SystemicInputs) -> RiskDirective:

        # 1) Hard interrupt first
        if self._hard_interrupt(inputs):
            return RiskDirective(
                mode=SystemicMode.SYSTEMIC,
                flatten_all=True,
                block_new_entries=True,
                increase_telemetry=True,
                reason="Hard interrupt triggered",
            )

        # 2) Composite regime path

        composite = (
            inputs.drawdown_velocity
            + inputs.liquidity_stress
            + inputs.correlation_spike
            + inputs.narrative_shock
            + inputs.structural_confirmation
        ) / 5.0

        if composite >= self.SYSTEMIC_THRESHOLD:
            return RiskDirective(
                mode=SystemicMode.SYSTEMIC,
                flatten_all=True,
                block_new_entries=True,
                increase_telemetry=True,
                reason="Composite systemic threshold breached",
            )

        if composite >= self.PRE_SYSTEMIC_THRESHOLD:
            return RiskDirective(
                mode=SystemicMode.PRE_SYSTEMIC,
                block_new_entries=True,
                increase_telemetry=True,
                reason="Pre-systemic escalation",
            )

        if composite >= self.STRESSED_THRESHOLD:
            return RiskDirective(
                mode=SystemicMode.STRESSED,
                increase_telemetry=True,
                reason="Stress regime",
            )

        return RiskDirective(
            mode=SystemicMode.NORMAL,
            reason="Normal regime",
        )