from marketmind_engine.orchestrator.intraday_orchestrator import IntradayOrchestrator
from marketmind_engine.regime.macro_sources.base import MacroInputSource
from marketmind_engine.regime.systemic_monitor import SystemicInputs


class DummySource(MacroInputSource):
    source_type = "test"

    def __init__(self):
        self.value = 0.0

    def collect(self):
        v = self.value
        return SystemicInputs(v, v, v, v, v)


source = DummySource()
orch = IntradayOrchestrator(macro_source=source)

print("\n--- SYSTEMIC SHOCK ---")
source.value = 0.90  # systemic
print(orch.run_cycle())

print("\n--- RECOVERY START ---")
source.value = 0.40  # calm
print(orch.run_cycle())

print("\n--- RECOVERY PROGRESSION ---")
for i in range(6):
    print(f"Cycle {i+1}")
    print(orch.run_cycle())