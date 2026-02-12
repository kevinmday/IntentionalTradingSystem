from dataclasses import dataclass
from typing import Dict

from marketmind_engine.execution.position import Position
from marketmind_engine.agents.agent_signal import AgentSignal


@dataclass
class PositionAgent:
    """
    Engine-level lifecycle controller for a single open position.

    Emits AgentSignal only.
    Does NOT execute trades.
    Does NOT mutate portfolio.
    """

    position: Position

    def evaluate(self, market_context: Dict) -> AgentSignal:
        """
        Evaluate exit conditions for this position.

        market_context should include:
            - price
            - fils
            - ttcf
            - drift
        """

        symbol = self.position.symbol

        price = market_context.get("price", self.position.average_entry_price)
        fils = market_context.get("fils", 0)
        ttcf = market_context.get("ttcf", 0)
        drift = market_context.get("drift", 0)

        entry_price = self.position.average_entry_price

        # -------------------------------------------------
        # PHASE 9 — Minimal Deterministic Exit Logic
        # -------------------------------------------------

        # 1. Hard stop (10% default fallback guard)
        if price < entry_price * 0.90:
            return AgentSignal(
                symbol=symbol,
                action="EXIT",
                reason="Hard stop breach",
                confidence=1.0,
            )

        # 2. Chaos inversion (TTCF breach)
        if ttcf > 0.18:
            return AgentSignal(
                symbol=symbol,
                action="EXIT",
                reason="TTCF inversion",
                confidence=0.85,
            )

        # 3. Narrative decay
        if fils < 50:
            return AgentSignal(
                symbol=symbol,
                action="EXIT",
                reason="Narrative decay",
                confidence=0.75,
            )

        # 4. Drift divergence
        if drift < 0:
            return AgentSignal(
                symbol=symbol,
                action="EXIT",
                reason="Negative drift",
                confidence=0.60,
            )

        # Default: hold
        return AgentSignal(
            symbol=symbol,
            action="HOLD",
            reason="Conditions stable",
            confidence=0.5,
        )