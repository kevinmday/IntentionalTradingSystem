from time import time

from marketmind_engine.runtime.trade_coordinator import TradeCoordinator
from marketmind_engine.orchestrator.intraday_orchestrator import IntradayOrchestrator
from marketmind_engine.execution.execution_engine import ExecutionEngine
from marketmind_engine.execution.execution_input import ExecutionInput
from marketmind_engine.regime.macro_sources.injected_source import InjectedMacroSource


# ------------------------------------------------------
# Minimal Dummy Objects (Deterministic)
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
        engine_time=time(),
    )


engine = ExecutionEngine()


# ------------------------------------------------------
# 1️⃣ STANDBY (Should Block)
# ------------------------------------------------------

stressed_inputs = {
    "drawdown_velocity": 1.0,
    "liquidity_stress": 1.0,
    "correlation_spike": 1.0,
    "narrative_shock": 1.0,
    "structural_confirmation": 1.0,
}

orchestrator = IntradayOrchestrator(
    macro_source=InjectedMacroSource(stressed_inputs)
)

coordinator = TradeCoordinator(orchestrator, engine)

print("Testing STANDBY block...")
result = coordinator.run(build_execution_input())
print(result)
print()


# ------------------------------------------------------
# 2️⃣ NORMAL (Should Allow Full Size)
# ------------------------------------------------------

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

coordinator = TradeCoordinator(orchestrator, engine)

print("Testing NORMAL allow...")
result = coordinator.run(build_execution_input())
print(result)
print()


# ------------------------------------------------------
# 3️⃣ PRE_SYSTEMIC (Should Reduce Size)
# ------------------------------------------------------

pre_systemic_inputs = {
    "drawdown_velocity": 0.75,
    "liquidity_stress": 0.75,
    "correlation_spike": 0.75,
    "narrative_shock": 0.75,
    "structural_confirmation": 0.75,
}

orchestrator = IntradayOrchestrator(
    macro_source=InjectedMacroSource(pre_systemic_inputs)
)

coordinator = TradeCoordinator(orchestrator, engine)

print("Testing PRE_SYSTEMIC size reduction...")
result = coordinator.run(build_execution_input())
print(result)
print()