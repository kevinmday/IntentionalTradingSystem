from marketmind_engine.orchestrator.intraday_orchestrator import IntradayOrchestrator
from marketmind_engine.regime.macro_sources.base import MacroInputSource
from marketmind_engine.regime.systemic_monitor import SystemicInputs


class DummySource(MacroInputSource):
    source_type = "test"

    def collect(self):
        return SystemicInputs(0, 0, 0, 0, 0)


orch = IntradayOrchestrator(macro_source=DummySource())

tests = [0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.85, 0.90]

for s in tests:
    orch._macro_source.collect = lambda s=s: SystemicInputs(s, s, s, s, s)
    result = orch.run_cycle()
    regime = result["regime"]
    mult = result["execution"]["size_multiplier"]
    print(f"{s:.2f} -> {regime}, {mult:.3f}")