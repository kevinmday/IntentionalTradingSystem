from typing import Optional, List

from marketmind_engine.orchestrator.intraday_orchestrator import IntradayOrchestrator
from marketmind_engine.execution.execution_engine import ExecutionEngine
from marketmind_engine.execution.execution_input import ExecutionInput
from marketmind_engine.execution.execution_types import OrderIntent

from marketmind_engine.agents.lifecycle_manager import AgentLifecycleManager
from marketmind_engine.agents.agent_signal import AgentSignal
from marketmind_engine.execution.position_snapshot import PositionSnapshot

from marketmind_engine.narrative.narrative_adapter import NarrativeAdapter


class TradeCoordinator:
    """
    Phase 13 — Projection Integrated (Controlled)

    Authority hierarchy:
        EXIT > ENTRY

    Projection feeds attention only.
    """

    def __init__(
        self,
        orchestrator: IntradayOrchestrator,
        execution_engine: ExecutionEngine,
        narrative_adapter: Optional[NarrativeAdapter] = None,
    ):
        self._orchestrator = orchestrator
        self._execution_engine = execution_engine
        self._lifecycle_manager = AgentLifecycleManager()

        # Optional narrative injection
        self._narrative_adapter = narrative_adapter

    # --------------------------------------------------
    # PROJECTION ROUTING (ATTENTION ONLY)
    # --------------------------------------------------

    def _route_projection_events(self):

        if not self._narrative_adapter:
            return

        events = self._narrative_adapter.get_projection_events()

        for event in events:
            self._lifecycle_manager.route_rss_event(
                {
                    "symbol": event.symbol,
                    "engine_time": event.engine_time,
                    "source": event.source,
                    "sentiment": event.sentiment,
                }
            )

    # --------------------------------------------------
    # EXIT AUTHORITY
    # --------------------------------------------------

    def _resolve_exit_intent(
        self,
        position_snapshot: PositionSnapshot,
        market_context_map: dict,
    ) -> Optional[OrderIntent]:

        self._lifecycle_manager.sync_with_portfolio(position_snapshot)

        signals: List[AgentSignal] = self._lifecycle_manager.evaluate_all(
            market_context_map
        )

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

    # --------------------------------------------------
    # MAIN RUN LOOP
    # --------------------------------------------------

    def run(
        self,
        execution_input: ExecutionInput,
        market_context_map: Optional[dict] = None,
    ) -> dict:

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
        # 2. Projection Routing (Narrative → Attention)
        # --------------------------------------------------

        self._route_projection_events()

        # --------------------------------------------------
        # 3. EXIT Authority
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
        # 4. ENTRY Authority
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
