from marketmind_engine.regime.systemic_mode import SystemicMode
from .base import RegimeExecutionPolicy, ExecutionDirective


class DefaultRegimeExecutionPolicy(RegimeExecutionPolicy):

    def resolve(self, regime: SystemicMode) -> ExecutionDirective:

        if regime == SystemicMode.NORMAL:
            return ExecutionDirective(True, 1.0, "normal")

        if regime == SystemicMode.STANDBY:
            return ExecutionDirective(False, 0.0, "capital_preservation")

        if regime == SystemicMode.PRE_SYSTEMIC:
            return ExecutionDirective(True, 0.5, "elevated")

        if regime == SystemicMode.SYSTEMIC:
            return ExecutionDirective(False, 0.0, "systemic_lockdown")

        return ExecutionDirective(False, 0.0, "unknown")
