from typing import Optional, Dict, Any

from marketmind_engine.runtime.runtime_executor import RuntimeExecutor
from marketmind_engine.execution.execution_input import ExecutionInput
from marketmind_engine.runtime.execution_input_factory import ExecutionInputFactory


class EngineController:
    """
    Manual-trigger engine controller.

    Responsibilities:
        • Hold RuntimeExecutor
        • Hold ExecutionInputFactory
        • Execute one cycle on demand
        • Store last result
        • Expose engine state

    No intelligence.
    No lifecycle mutation.
    No threading.
    No background loop.
    """

    def __init__(
        self,
        runtime_executor: RuntimeExecutor,
        execution_input_factory: ExecutionInputFactory,
    ):
        self._executor = runtime_executor
        self._factory = execution_input_factory
        self._last_result: Optional[Dict[str, Any]] = None
        self._running: bool = False

    # --------------------------------------------------
    # Lifecycle
    # --------------------------------------------------

    def start(self) -> None:
        self._running = True

    def stop(self) -> None:
        self._running = False

    def is_running(self) -> bool:
        return self._running

    # --------------------------------------------------
    # Low-Level Execution (Existing Behavior)
    # --------------------------------------------------

    def run_once(
        self,
        execution_input: ExecutionInput,
        market_context_map: Optional[dict] = None,
    ) -> Dict[str, Any]:

        if not self._running:
            raise RuntimeError("Engine is not started.")

        result = self._executor.run_cycle(
            execution_input,
            market_context_map=market_context_map,
        )

        self._last_result = result
        return result

    # --------------------------------------------------
    # High-Level Browser Trigger
    # --------------------------------------------------

    def run_symbol_cycle(
        self,
        symbol: str,
        market_context_map: Optional[dict] = None,
    ) -> Dict[str, Any]:
        """
        High-level trigger for API/browser usage.

        Constructs ExecutionInput via factory,
        then delegates to RuntimeExecutor.
        """

        if not self._running:
            raise RuntimeError("Engine is not started.")

        # Advance deterministic runtime clock (1 second per manual cycle)
        self._factory.clock.advance(1)

        execution_input = self._factory.build_for_symbol(symbol)

        result = self._executor.run_cycle(
            execution_input,
            market_context_map=market_context_map,
        )

        self._last_result = result
        return result

    # --------------------------------------------------
    # Snapshot
    # --------------------------------------------------

    def get_last_result(self) -> Optional[Dict[str, Any]]:
        return self._last_result