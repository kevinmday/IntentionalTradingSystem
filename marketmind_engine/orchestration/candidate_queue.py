from dataclasses import dataclass, field
from typing import Dict, List, Optional
import heapq
import time


@dataclass(order=True)
class Candidate:
    sort_index: float = field(init=False, repr=False)
    score: float
    timestamp: float
    symbol: str
    fils: float
    ucip: float
    ttcf: float
    drift: float
    sector: str
    narrative_tag: str

    def __post_init__(self):
        # Negative score for max-heap behavior using heapq (min-heap)
        self.sort_index = -self.score


class CandidateQueue:
    """
    Deterministic priority queue for intraday candidate rotation.
    Highest score always first.
    """

    def __init__(self):
        self._heap: List[Candidate] = []
        self._lookup: Dict[str, Candidate] = {}

    def add(self, candidate: Candidate):
        if candidate.symbol in self._lookup:
            return
        heapq.heappush(self._heap, candidate)
        self._lookup[candidate.symbol] = candidate

    def remove(self, symbol: str):
        if symbol not in self._lookup:
            return
        candidate = self._lookup.pop(symbol)
        self._heap.remove(candidate)
        heapq.heapify(self._heap)

    def update_score(self, symbol: str, new_score: float):
        if symbol not in self._lookup:
            return
        candidate = self._lookup[symbol]
        self.remove(symbol)
        updated = Candidate(
            score=new_score,
            timestamp=candidate.timestamp,
            symbol=candidate.symbol,
            fils=candidate.fils,
            ucip=candidate.ucip,
            ttcf=candidate.ttcf,
            drift=candidate.drift,
            sector=candidate.sector,
            narrative_tag=candidate.narrative_tag,
        )
        self.add(updated)

    def get_next(self, exclude: Optional[set] = None) -> Optional[Candidate]:
        if not self._heap:
            return None

        exclude = exclude or set()

        temp = []
        selected = None

        while self._heap:
            candidate = heapq.heappop(self._heap)
            if candidate.symbol not in exclude:
                selected = candidate
                break
            temp.append(candidate)

        for item in temp:
            heapq.heappush(self._heap, item)

        if selected:
            self._lookup.pop(selected.symbol, None)

        return selected

    def get_ranked_list(self) -> List[Candidate]:
        return sorted(self._heap)

    def clear(self):
        self._heap.clear()
        self._lookup.clear()

    def __len__(self):
        return len(self._heap)

