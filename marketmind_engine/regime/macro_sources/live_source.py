from marketmind_engine.regime.macro_sources.base import MacroInputSource
from marketmind_engine.regime.systemic_monitor import SystemicInputs


class LiveMacroSource(MacroInputSource):
    """
    Live macro input source.

    Owns its own collection logic.
    No external callable required.
    """

    source_type = "live"

    def __init__(self):
        pass

    def collect(self) -> SystemicInputs:
        """
        Collect live systemic inputs.

        Replace placeholder values with real data feeds later.
        """

        # TEMP deterministic placeholders
        return SystemicInputs(
            drawdown_velocity=0.1,
            liquidity_stress=0.1,
            correlation_spike=0.1,
            narrative_shock=0.1,
            structural_confirmation=0.1,
        )