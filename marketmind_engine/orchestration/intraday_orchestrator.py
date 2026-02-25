from typing import List, Optional, Set

from marketmind_engine.orchestration.candidate_queue import CandidateQueue, Candidate
from marketmind_engine.orchestration.entry_gate import EntryGate
from marketmind_engine.state.contracts import MarketState


class IntradayOrchestrator:
    """
    Coordinates candidate rotation and entry gating.
    Does NOT execute trades.
    Does NOT compute signals.
    Pure orchestration layer.
    """

    def __init__(
        self,
        entry_gate: EntryGate,
        max_positions: int = 3,
    ):
        self.entry_gate = entry_gate
        self.queue = CandidateQueue()
        self.active_positions: Set[str] = set()
        self.max_positions = max_positions

    # ---------------------------
    # Candidate Management
    # ---------------------------

    def add_candidate(self, candidate: Candidate):
        if candidate.symbol not in self.active_positions:
            self.queue.add(candidate)

    def get_queue_size(self) -> int:
        return len(self.queue)

    # ---------------------------
    # Entry Attempt Logic
    # ---------------------------

    def attempt_entries(self, state_lookup: dict) -> List[str]:
        """
        Attempt to enter positions from queue.
        state_lookup: dict[symbol] -> MarketState

        Returns list of symbols allowed for entry.
        """
        entered = []

        if len(self.active_positions) >= self.max_positions:
            return entered

        while len(self.active_positions) < self.max_positions:

            candidate = self.queue.get_next(exclude=self.active_positions)

            if not candidate:
                break

            state: Optional[MarketState] = state_lookup.get(candidate.symbol)

            if not state:
                continue

            decision = self.entry_gate.evaluate(state)

            if decision.allow:
                self.active_positions.add(candidate.symbol)
                entered.append(candidate.symbol)
            else:
                # If blocked, do not requeue immediately
                pass

        return entered

    # ---------------------------
    # Exit Handling
    # ---------------------------

    def register_exit(self, symbol: str):
        """
        Called when a position is flattened.
        Frees slot for next candidate.
        """
        if symbol in self.active_positions:
            self.active_positions.remove(symbol)

    # ---------------------------
    # State Introspection
    # ---------------------------

    def get_active_positions(self) -> Set[str]:
        return set(self.active_positions)