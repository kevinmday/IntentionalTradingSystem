from typing import Optional, Dict, Any

from marketmind_engine.runtime.runtime_executor import RuntimeExecutor
from marketmind_engine.execution.execution_input import ExecutionInput


class EngineController:
    """
    Manual-trigger engine controller.

    Responsibilities:
        • Hold RuntimeExecutor
        • Execute one cycle on demand
        • Store last result
        • Expose engine state

    No intelligence.
    No lifecycle mutation.
    No threading.
    No background loop.
    """

    def __init__(self, runtime_executor: RuntimeExecutor):
        self._executor = runtime_executor
        self._last_result: Optional[Dict[str, Any]] = None
        self._running: bool = False

    def start(self) -> None:
        self._running = True

    def stop(self) -> None:
        self._running = False

    def is_running(self) -> bool:
        return self._running

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

    def get_last_result(self) -> Optional[Dict[str, Any]]:
        return self._last_result