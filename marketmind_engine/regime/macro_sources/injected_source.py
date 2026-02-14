from typing import Dict

from marketmind_engine.regime.systemic_monitor import SystemicInputs


class InjectedMacroSource:
    """
    Static deterministic macro override.

    Converts injected dict payload into SystemicInputs
    to preserve contract with SystemicMonitor.
    """

    def __init__(self, macro_inputs: Dict):
        if not isinstance(macro_inputs, dict):
            raise ValueError("InjectedMacroSource requires full macro payload dict")

        required_fields = [
            "drawdown_velocity",
            "liquidity_stress",
            "correlation_spike",
            "narrative_shock",
            "structural_confirmation",
        ]

        for field in required_fields:
            if field not in macro_inputs:
                raise ValueError(f"Missing required macro input field: {field}")

        # Convert dict → SystemicInputs
        self._macro_inputs = SystemicInputs(
            drawdown_velocity=macro_inputs["drawdown_velocity"],
            liquidity_stress=macro_inputs["liquidity_stress"],
            correlation_spike=macro_inputs["correlation_spike"],
            narrative_shock=macro_inputs["narrative_shock"],
            structural_confirmation=macro_inputs["structural_confirmation"],
        )

    def collect(self) -> SystemicInputs:
        return self._macro_inputs

    @property
    def source_type(self) -> str:
        return "injected"