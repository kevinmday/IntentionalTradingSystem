from dataclasses import dataclass
from typing import Dict, Optional, List

from marketmind_engine.state.contracts import MarketState
from marketmind_engine.orchestration.exit_policy_engine import ExitTriggerEvent


# ----------------------------------------
# PositionAgent
# ----------------------------------------

class PositionAgent:
    """
    Dedicated lifecycle agent for a single open position.
    Detects degradation conditions and emits ExitTriggerEvent.
    """

    def __init__(self, symbol: str, entry_price: float, entry_time: int):
        self.symbol = symbol
        self.entry_price = entry_price
        self.entry_time = entry_time

        self.peak_price = entry_price
        self.monitoring_tier = 2  # default active position tier

    # ---------------------------
    # State Update Hook
    # ---------------------------

    def update(self, state: MarketState) -> Optional[ExitTriggerEvent]:

        if state.price is None:
            return None

        # Update peak tracking
        if state.price > self.peak_price:
            self.peak_price = state.price

        # --- HARD STOP (2% loss) ---
        pnl = (state.price - self.entry_price) / self.entry_price
        if pnl <= -0.02:
            return self._build_trigger(state, "HARD_STOP")

        # --- DRIFT COLLAPSE ---
        if state.drift < 0.010:
            return self._build_trigger(state, "DRIFT_COLLAPSE")

        # --- CHAOS ESCALATION ---
        if state.ttcf > 0.22:
            return self._build_trigger(state, "CHAOS_ESCALATION")

        # --- PEAK GIVEBACK (1.5% retrace) ---
        retrace = (state.price - self.peak_price) / self.peak_price
        if retrace <= -0.015:
            return self._build_trigger(state, "PEAK_GIVEBACK")

        return None

    # ---------------------------
    # Trigger Builder
    # ---------------------------

    def _build_trigger(self, state: MarketState, trigger_type: str) -> ExitTriggerEvent:

        return ExitTriggerEvent(
            symbol=self.symbol,
            trigger_type=trigger_type,
            engine_time=state.engine_time,
            price=state.price,
            entry_price=self.entry_price,
            peak_price=self.peak_price,
            drift=state.drift,
            ttcf=state.ttcf,
            delta_since_ignition=state.delta_since_ignition,
            monitoring_tier=self.monitoring_tier,
        )

    # ---------------------------
    # Tier Reporting
    # ---------------------------

    def get_monitoring_tier(self) -> int:
        return self.monitoring_tier


# ----------------------------------------
# PositionManager
# ----------------------------------------

class PositionManager:
    """
    Coordinates multiple PositionAgents.
    Routes state updates and collects exit trigger events.
    """

    def __init__(self):
        self.agents: Dict[str, PositionAgent] = {}

    # ---------------------------
    # Register Entry
    # ---------------------------

    def register_entry(self, state: MarketState):
        if state.symbol not in self.agents:
            agent = PositionAgent(
                symbol=state.symbol,
                entry_price=state.price,
                entry_time=state.engine_time,
            )
            self.agents[state.symbol] = agent

    # ---------------------------
    # Process State Updates
    # ---------------------------

    def process_updates(self, state_lookup: Dict[str, MarketState]) -> List[ExitTriggerEvent]:

        triggers: List[ExitTriggerEvent] = []

        for symbol, agent in self.agents.items():

            state = state_lookup.get(symbol)
            if not state:
                continue

            trigger = agent.update(state)

            if trigger:
                triggers.append(trigger)

        return triggers

    # ---------------------------
    # Remove Position (after policy directive)
    # ---------------------------

    def remove_position(self, symbol: str):
        if symbol in self.agents:
            del self.agents[symbol]

    # ---------------------------
    # Introspection
    # ---------------------------

    def get_active_symbols(self) -> List[str]:
        return list(self.agents.keys())