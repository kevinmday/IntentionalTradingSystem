"""
Authoritative Engine Assembly Harness

Builds full runtime stack:

MacroSource
→ IntradayOrchestrator
→ ExecutionEngine
→ TradeCoordinator
→ ExecutionService
→ RuntimeExecutor
→ EngineController
"""

from marketmind_engine.runtime.engine_controller import EngineController
from marketmind_engine.runtime.runtime_executor import RuntimeExecutor
from marketmind_engine.runtime.trade_coordinator import TradeCoordinator

from marketmind_engine.execution.execution_engine import ExecutionEngine
from marketmind_engine.execution.execution_service import ExecutionService

from marketmind_engine.orchestrator.intraday_orchestrator import IntradayOrchestrator

from marketmind_engine.regime.macro_sources.injected_source import InjectedMacroSource
from marketmind_engine.broker.paper_adapter import PaperBrokerAdapter


def build_engine() -> EngineController:
    """
    Deterministic activation build.

    Uses injected neutral macro regime.
    """

    # --------------------------------------------------
    # 1. Neutral Macro Source (Activation Mode)
    # --------------------------------------------------

    macro_source = InjectedMacroSource(
        {
            "drawdown_velocity": 0.0,
            "liquidity_stress": 0.0,
            "correlation_spike": 0.0,
            "narrative_shock": 0.0,
            "structural_confirmation": 0.0,
        }
    )

    # --------------------------------------------------
    # 2. Core Engine Components
    # --------------------------------------------------

    execution_engine = ExecutionEngine()

    orchestrator = IntradayOrchestrator(
        macro_source=macro_source,
        portfolio=None,
        execution_engine=execution_engine,
        audit_writer=None,
    )

    coordinator = TradeCoordinator(
        orchestrator=orchestrator,
        execution_engine=execution_engine,
        narrative_adapter=None,
    )

    # --------------------------------------------------
    # 3. Paper Broker Injection
    # --------------------------------------------------

    broker = PaperBrokerAdapter()
    execution_service = ExecutionService(broker=broker)

    runtime_executor = RuntimeExecutor(
        coordinator=coordinator,
        execution_service=execution_service,
    )

    engine_controller = EngineController(runtime_executor)

    return engine_controller