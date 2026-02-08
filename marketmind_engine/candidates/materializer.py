from typing import Iterable, List
from marketmind_engine.candidates.types import Candidate
from marketmind_engine.candidates.builder import materialize_candidate
from marketmind_engine.decision.decision_engine import DecisionEngine
from marketmind_engine.decision.state import MarketState


def materialize_candidates(
    states: Iterable[MarketState],
) -> List[Candidate]:
    engine = DecisionEngine()

    return [
        materialize_candidate(state, engine)
        for state in states
    ]