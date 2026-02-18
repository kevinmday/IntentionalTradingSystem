from typing import Optional, List

from marketmind_engine.orchestrator.intraday_orchestrator import IntradayOrchestrator
from marketmind_engine.execution.execution_engine import ExecutionEngine
from marketmind_engine.execution.execution_input import ExecutionInput
from marketmind_engine.execution.execution_types import OrderIntent

from marketmind_engine.agents.lifecycle_manager import AgentLifecycleManager
from marketmind_engine.agents.agent_signal import AgentSignal
from marketmind_engine.execution.position_snapshot import PositionSnapshot


class TradeCoordinator:
    """
    Phase 12.3 — Lifecycle Integrated

    Bridges:
        Orchestrator
        AgentLifecycleManager (exit authority)
        ExecutionEngine (entry authority)

    Authority hierarchy:
        EXIT > ENTRY

    Deterministic.
    No hidden loops.
    No capital mutation here.
    """

    def __init__(
        self,
        orchestrator: IntradayOrchestrator,
        execution_engine: ExecutionEngine,
    ):
        self._orchestrator = orchestrator
        self._execution_engine = execution_engine
        self._lifecycle_manager = AgentLifecycleManager()

    def _resolve_exit_intent(
        self,
        position_snapshot: PositionSnapshot,
        market_context_map: dict,
    ) -> Optional[OrderIntent]:
        """
        Evaluate all position agents.
        If any EXIT signal occurs, return SELL OrderIntent.
        EXIT authority overrides entry.
        """

        # Sync lifecycle agents with current portfolio
        self._lifecycle_manager.sync_with_portfolio(position_snapshot)

        signals: List[AgentSignal] = self._lifecycle_manager.evaluate_all(
            market_context_map
        )

        # First EXIT wins (deterministic order)
        for signal in signals:
            if signal.action == "EXIT":
                position = position_snapshot.positions.get(signal.symbol)
                if not position:
                    continue

                return OrderIntent(
                    symbol=signal.symbol,
                    side="sell",
                    order_type="market",
                    quantity=position.quantity,
                    rationale=signal.reason,
                    confidence=signal.confidence,
                )

        return None

    def run(
        self,
        execution_input: ExecutionInput,
        market_context_map: Optional[dict] = None,
    ) -> dict:
        """
        Single deterministic evaluation cycle.

        Order of operations:
            1. Regime authority
            2. Exit authority (PositionAgents)
            3. Entry authority (ExecutionEngine)
        """

        # --------------------------------------------------
        # 1. Regime Authority
        # --------------------------------------------------

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

        # --------------------------------------------------
        # 2. EXIT Authority (Quant-driven)
        # --------------------------------------------------

        exit_intent = None
        if market_context_map:
            exit_intent = self._resolve_exit_intent(
                execution_input.position_snapshot,
                market_context_map,
            )

        if exit_intent:
            return {
                "regime": regime_result,
                "order_intent": exit_intent,
                "authority": "EXIT",
            }

        # --------------------------------------------------
        # 3. ENTRY Authority (Narrative-driven)
        # --------------------------------------------------

        entry_intent: Optional[OrderIntent] = self._execution_engine.evaluate(
            execution_input,
            execution_directive=directive,
        )

        return {
            "regime": regime_result,
            "order_intent": entry_intent,
            "authority": "ENTRY" if entry_intent else None,
        }
