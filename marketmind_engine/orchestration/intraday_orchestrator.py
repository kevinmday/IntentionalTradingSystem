from typing import Dict, List, Set

from marketmind_engine.orchestration.candidate_queue import CandidateQueue
from marketmind_engine.orchestration.entry_gate import EntryGate
from marketmind_engine.orchestration.position_manager import PositionManager
from marketmind_engine.orchestration.exit_policy_engine import (
    ExitPolicyEngine,
    ExitTriggerEvent,
    PortfolioState,
)
from marketmind_engine.state.contracts import MarketState


class IntradayOrchestrator:
    """
    Coordinates full intraday lifecycle:
    - Entry evaluation
    - Position monitoring
    - Exit routing
    - Capital recycling
    """

    def __init__(self, entry_gate: EntryGate, max_positions: int = 3):
        self.entry_gate = entry_gate
        self.max_positions = max_positions

        self.queue = CandidateQueue()
        self.position_manager = PositionManager()
        self.exit_policy = ExitPolicyEngine()

        self.active_positions: Set[str] = set()

    # ---------------------------------
    # Candidate Intake
    # ---------------------------------

    def add_candidate(self, candidate):
        self.queue.add(candidate)

    # ---------------------------------
    # Entry Attempt
    # ---------------------------------

    def attempt_entries(self, state_lookup: Dict[str, MarketState]) -> List[str]:

        entered: List[str] = []

        while (
            len(self.active_positions) < self.max_positions
            and len(self.queue) > 0
        ):
            candidate = self.queue.get_next()
            state = state_lookup.get(candidate.symbol)

            if not state:
                continue

            decision = self.entry_gate.evaluate(state)

            if decision.allow:
                self.position_manager.register_entry(state)
                self.active_positions.add(candidate.symbol)
                entered.append(candidate.symbol)

        return entered

    # ---------------------------------
    # Position Monitoring + Exit Flow
    # ---------------------------------

    def process_updates(self, state_lookup: Dict[str, MarketState]) -> List[str]:

        exited: List[str] = []

        triggers = self.position_manager.process_updates(state_lookup)

        for trigger in triggers:

            portfolio_state = PortfolioState(
                total_capital=0.0,  # hook for future
                open_positions={symbol: 1.0 for symbol in self.active_positions},
                total_unrealized_pnl=0.0,
                systemic_risk_level=0.0,
            )

            directive = self.exit_policy.evaluate(trigger, portfolio_state)

            if directive.action == "FULL_EXIT":
                self.position_manager.remove_position(directive.symbol)
                self.active_positions.remove(directive.symbol)
                exited.append(directive.symbol)

            # PARTIAL_EXIT and others are future extension

        return exited

    # ---------------------------------
    # Introspection
    # ---------------------------------

    def get_active_positions(self) -> Set[str]:
        return set(self.active_positions)
