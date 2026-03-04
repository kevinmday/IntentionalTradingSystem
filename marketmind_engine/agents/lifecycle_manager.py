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
    - Routes RSS telemetry (observational only)

    No execution.
    No capital mutation.
    """

    def __init__(self, debug_attention: bool = False) -> None:
        self._agents: Dict[str, PositionAgent] = {}
        self._debug_attention = debug_attention

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

            # ---------------------------------------------
            # DEBUG ATTENTION TELEMETRY (NON-INVASIVE)
            # ---------------------------------------------
            if self._debug_attention:
                snapshot = agent.get_attention_snapshot()
                if snapshot:
                    print(
                        f"[ATTN] {symbol} | "
                        f"density={snapshot.density:.3f} | "
                        f"velocity={snapshot.velocity:.3f} | "
                        f"spread={snapshot.source_spread:.3f} | "
                        f"sentiment={snapshot.sentiment_bias:.3f}"
                    )

        return signals

    # -------------------------------------------------
    # RSS ROUTING (OBSERVATIONAL ONLY)
    # -------------------------------------------------

    def route_rss_event(self, event: Dict) -> None:
        """
        Forward symbol-specific RSS event to active agent.

        Expected event structure:
        {
            "symbol": str,
            "engine_time": int,
            "source": str,
            "sentiment": float
        }

        This does NOT influence exit logic in v1.
        """

        if not event:
            return

        symbol = event.get("symbol")
        if not symbol:
            return

        agent = self._agents.get(symbol)
        if not agent:
            return

        agent.on_rss_event(event)

    # -------------------------------------------------
    # Introspection
    # -------------------------------------------------

    def active_symbols(self) -> List[str]:
        return list(self._agents.keys())

    def get_attention_snapshot(self, symbol: str):
        """
        Optional inspection helper.
        Does not affect trading logic.
        """
        agent = self._agents.get(symbol)
        if not agent:
            return None

        return agent.get_attention_snapshot()
