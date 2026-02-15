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

    # Continuous scaling constant (Phase-12C)
    SCALING_K = 1.0  # full linear degradation across band

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
    # Continuous Scaling Logic (Phase-12C)
    # ----------------------------------------------------------

    def _compute_size_multiplier(
        self,
        composite_score: float,
        hard_interrupt: bool,
    ) -> float:
        """
        Continuous deterministic degradation between
        STRESSED_THRESHOLD and SYSTEMIC_THRESHOLD.

        Hard interrupt forces 0.
        Clamped between 0 and 1.
        """

        if hard_interrupt:
            return 0.0

        if composite_score < self.STRESSED_THRESHOLD:
            return 1.0

        if composite_score >= self.SYSTEMIC_THRESHOLD:
            return 0.0

        band = self.SYSTEMIC_THRESHOLD - self.STRESSED_THRESHOLD
        normalized = (composite_score - self.STRESSED_THRESHOLD) / band

        raw_multiplier = 1.0 - (normalized * self.SCALING_K)

        # Clamp safety
        return max(0.0, min(1.0, raw_multiplier))

    # ----------------------------------------------------------
    # Evaluation Entry Point
    # ----------------------------------------------------------

    def evaluate(self, inputs: SystemicInputs) -> RiskDirective:

        # 1) Hard interrupt first
        hard = self._hard_interrupt(inputs)

        if hard:
            return RiskDirective(
                mode=SystemicMode.SYSTEMIC,
                flatten_all=True,
                block_new_entries=True,
                size_multiplier=0.0,
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

        size_multiplier = self._compute_size_multiplier(
            composite_score=composite,
            hard_interrupt=False,
        )

        # SYSTEMIC (composite path)
        if composite >= self.SYSTEMIC_THRESHOLD:
            return RiskDirective(
                mode=SystemicMode.SYSTEMIC,
                flatten_all=True,
                block_new_entries=True,
                size_multiplier=0.0,
                increase_telemetry=True,
                reason="Composite systemic threshold breached",
            )

        # PRE_SYSTEMIC
        if composite >= self.PRE_SYSTEMIC_THRESHOLD:
            return RiskDirective(
                mode=SystemicMode.PRE_SYSTEMIC,
                block_new_entries=False,
                size_multiplier=size_multiplier,
                increase_telemetry=True,
                reason="Pre-systemic escalation",
            )

        # STRESSED
        if composite >= self.STRESSED_THRESHOLD:
            return RiskDirective(
                mode=SystemicMode.STRESSED,
                block_new_entries=False,
                size_multiplier=size_multiplier,
                increase_telemetry=True,
                reason="Stress regime",
            )

        # NORMAL
        return RiskDirective(
            mode=SystemicMode.NORMAL,
            size_multiplier=1.0,
            reason="Normal regime",
        )