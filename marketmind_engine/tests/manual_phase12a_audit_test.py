from pathlib import Path

from marketmind_engine.orchestrator.intraday_orchestrator import IntradayOrchestrator
from marketmind_engine.regime.macro_sources.injected_source import InjectedMacroSource
from marketmind_engine.regime.audit.writer import RegimeAuditWriter


def main():

    # --------------------------------------------------
    # 1?? Create stressed injected macro inputs
    # --------------------------------------------------

    stressed_inputs = {
        "drawdown_velocity": 1.0,
        "liquidity_stress": 1.0,
        "correlation_spike": 1.0,
        "narrative_shock": 1.0,
        "structural_confirmation": 1.0,
    }

    macro_source = InjectedMacroSource(stressed_inputs)

    # --------------------------------------------------
    # 2?? Wire audit writer
    # --------------------------------------------------

    audit_writer = RegimeAuditWriter(
        Path("regime_logs/regime_transitions.jsonl")
    )

    # --------------------------------------------------
    # 3?? Instantiate orchestrator
    # --------------------------------------------------

    orchestrator = IntradayOrchestrator(
        macro_source=macro_source,
        audit_writer=audit_writer,
    )

    # --------------------------------------------------
    # 4?? Run cycle
    # --------------------------------------------------

    print("Running stressed cycle...")
    result = orchestrator.run_cycle()
    print(result)

    print("Done.")


if __name__ == "__main__":
    main()
