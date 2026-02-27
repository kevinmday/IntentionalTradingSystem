"""
Authoritative Engine Assembly Harness

Builds full runtime stack:

MacroSource
→ IntradayOrchestrator
→ ExecutionEngine
→ TradeCoordinator
→ ExecutionService
→ RuntimeExecutor
→ ExecutionInputFactory
→ EngineController
"""

from marketmind_engine.runtime.engine_controller import EngineController
from marketmind_engine.runtime.runtime_executor import RuntimeExecutor
from marketmind_engine.runtime.trade_coordinator import TradeCoordinator
from marketmind_engine.runtime.execution_input_factory import ExecutionInputFactory

from marketmind_engine.execution.execution_engine import ExecutionEngine
from marketmind_engine.execution.execution_service import ExecutionService

from marketmind_engine.orchestrator.intraday_orchestrator import IntradayOrchestrator

from marketmind_engine.regime.macro_sources.injected_source import InjectedMacroSource
from marketmind_engine.broker.paper_adapter import PaperBrokerAdapter


# ----------------------------------------------------------------------
# Minimal Stub Services (Deterministic Activation Mode)
# ----------------------------------------------------------------------

class StubCapitalService:
    def snapshot(self):
        return {}


class StubPositionService:
    def snapshot(self, symbol: str):
        return None


class StubPriceService:
    def get_price(self, symbol: str) -> float:
        return 100.0  # deterministic placeholder


class StubClock:
    def now(self) -> int:
        return 0  # deterministic activation time


class StubRegimeService:
    def current_state(self):
        return type("RegimeState", (), {"domain": "neutral"})()


class StubPolicyEngine:
    def evaluate(self, market_state):
        """
        Deterministic neutral policy result.

        Provides required attributes expected downstream.
        """

        return type(
            "PolicyResult",
            (),
            {
                "action": "HOLD",
                "confidence": 0.0,
                "reason": "Stub neutral policy",
            },
        )()


# ----------------------------------------------------------------------
# Build Engine
# ----------------------------------------------------------------------

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

    # --------------------------------------------------
    # 4. Snapshot Services
    # --------------------------------------------------

    capital_service = StubCapitalService()
    position_service = StubPositionService()
    price_service = StubPriceService()
    clock = StubClock()
    regime_service = StubRegimeService()
    policy_engine = StubPolicyEngine()

    execution_input_factory = ExecutionInputFactory(
        regime_service=regime_service,
        policy_engine=policy_engine,
        capital_service=capital_service,
        position_service=position_service,
        price_service=price_service,
        clock=clock,
    )

    # --------------------------------------------------
    # 5. Engine Controller
    # --------------------------------------------------

    engine_controller = EngineController(
        runtime_executor=runtime_executor,
        execution_input_factory=execution_input_factory,
    )

    return engine_controller