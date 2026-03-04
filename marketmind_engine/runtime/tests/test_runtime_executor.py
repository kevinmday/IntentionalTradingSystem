from datetime import datetime, UTC

from marketmind_engine.runtime.trade_coordinator import TradeCoordinator
from marketmind_engine.runtime.runtime_executor import RuntimeExecutor
from marketmind_engine.execution.execution_engine import ExecutionEngine
from marketmind_engine.execution.execution_input import ExecutionInput
from marketmind_engine.execution.execution_receipt import ExecutionReceipt
from marketmind_engine.execution.execution_types import OrderIntent
from marketmind_engine.execution.execution_service import ExecutionService
from marketmind_engine.broker.broker_adapter import BrokerAdapter
from marketmind_engine.orchestrator.intraday_orchestrator import IntradayOrchestrator
from marketmind_engine.regime.macro_sources.injected_source import InjectedMacroSource


# ------------------------------------------------------
# Deterministic Fake Broker
# ------------------------------------------------------

class FakeBrokerAdapter(BrokerAdapter):

    @property
    def name(self) -> str:
        return "FakeBroker"

    def submit(self, order_intent: OrderIntent) -> ExecutionReceipt:
        return ExecutionReceipt(
            broker_name=self.name,
            symbol=order_intent.symbol,
            side=order_intent.side,
            quantity=order_intent.quantity,
            order_type=order_intent.order_type,
            broker_order_id="RUNTIME-FAKE",
            accepted=True,
            message="Runtime test execution",
            timestamp_utc=datetime.now(UTC),
        )


# ------------------------------------------------------
# Minimal deterministic inputs
# ------------------------------------------------------

class DummyPolicyResult:
    def __init__(self):
        from marketmind_engine.policy.policy_types import PolicyAction
        self.action = PolicyAction.ALLOW
        self.confidence = 1.0


class DummyMarketState:
    def __init__(self):
        self.symbol = "TEST"


class DummyCapitalSnapshot:
    def __init__(self):
        self.account_equity = 100000
        self.max_risk_per_trade = 0.01
        self.buying_power = 100000


class DummyPositionSnapshot:
    def __init__(self):
        self.positions = {}


def build_execution_input():
    return ExecutionInput(
        policy_result=DummyPolicyResult(),
        market_state=DummyMarketState(),
        capital_snapshot=DummyCapitalSnapshot(),
        position_snapshot=DummyPositionSnapshot(),
        current_price=100.0,
        stop_price=95.0,
        engine_time=0,
    )


def test_runtime_executor_entry_flow():

    normal_inputs = {
        "drawdown_velocity": 0.0,
        "liquidity_stress": 0.0,
        "correlation_spike": 0.0,
        "narrative_shock": 0.0,
        "structural_confirmation": 0.0,
    }

    orchestrator = IntradayOrchestrator(
        macro_source=InjectedMacroSource(normal_inputs)
    )

    engine = ExecutionEngine()
    coordinator = TradeCoordinator(orchestrator, engine)

    broker = FakeBrokerAdapter()
    execution_service = ExecutionService(broker)

    runtime = RuntimeExecutor(coordinator, execution_service)

    result = runtime.run_cycle(build_execution_input())

    assert result["order_intent"] is not None
    assert result["execution_receipt"] is not None
    assert result["execution_receipt"].accepted is True
    assert result["execution_receipt"].broker_order_id == "RUNTIME-FAKE"
