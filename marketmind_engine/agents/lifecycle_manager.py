from typing import Dict, List

from marketmind_engine.execution.position_snapshot import PositionSnapshot
from marketmind_engine.agents.position_agent import PositionAgent
from marketmind_engine.agents.agent_signal import AgentSignal


class AgentLifecycleManager:
    """
    Orchestrates PositionAgents for all open positions.

    - Creates agents for new positions
    - Removes agents for closed positions
    - Evaluates all agents
    - Emits AgentSignals only

    No execution.
    No capital mutation.
    """

    def __init__(self) -> None:
        self._agents: Dict[str, PositionAgent] = {}

    # -------------------------------------------------
    # Portfolio Sync
    # -------------------------------------------------

    def sync_with_portfolio(self, snapshot: PositionSnapshot) -> None:
        """
        Ensure agent set matches current open positions.
        """

        # Add agents for new positions
        for symbol, position in snapshot.positions.items():
            if symbol not in self._agents:
                self._agents[symbol] = PositionAgent(position)

        # Remove agents for closed positions
        for symbol in list(self._agents.keys()):
            if symbol not in snapshot.positions:
                del self._agents[symbol]

    # -------------------------------------------------
    # Evaluation
    # -------------------------------------------------

    def evaluate_all(
        self,
        market_context_map: Dict[str, Dict],
    ) -> List[AgentSignal]:
        """
        Evaluate all active agents.

        market_context_map:
            {
                "AAPL": {"price": ..., "fils": ..., "ttcf": ..., "drift": ...},
                ...
            }
        """

        signals: List[AgentSignal] = []

        for symbol, agent in self._agents.items():
            context = market_context_map.get(symbol, {})
            signal = agent.evaluate(context)
            signals.append(signal)

        return signals

    # -------------------------------------------------
    # Introspection
    # -------------------------------------------------

    def active_symbols(self) -> List[str]:
        return list(self._agents.keys())