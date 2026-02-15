from typing import Optional

from marketmind_engine.orchestrator.intraday_orchestrator import IntradayOrchestrator
from marketmind_engine.execution.execution_engine import ExecutionEngine
from marketmind_engine.execution.execution_input import ExecutionInput
from marketmind_engine.execution.execution_types import OrderIntent


class TradeCoordinator:
    """
    Phase 12.2

    Bridges:
        Orchestrator ? ExecutionDirective ? ExecutionEngine

    No authority mutation.
    No hidden coupling.
    Deterministic coordination only.
    """

    def __init__(
        self,
        orchestrator: IntradayOrchestrator,
        execution_engine: ExecutionEngine,
    ):
        self._orchestrator = orchestrator
        self._execution_engine = execution_engine

    def run(
        self,
        execution_input: ExecutionInput,
    ) -> dict:
        """
        1. Run authority cycle
        2. Resolve execution directive
        3. Evaluate execution engine
        """

        regime_result = self._orchestrator.run_cycle()

        execution_block = regime_result.get("execution")

        directive = None
        if execution_block:
            from marketmind_engine.execution.policy.base import ExecutionDirective

            directive = ExecutionDirective(
                allow_entries=execution_block["allow_entries"],
                size_multiplier=execution_block["size_multiplier"],
                risk_level=execution_block["risk_level"],
            )

        order: Optional[OrderIntent] = self._execution_engine.evaluate(
            execution_input,
            execution_directive=directive,
        )

        return {
            "regime": regime_result,
            "order_intent": order,
        }
