from collections import deque
from dataclasses import dataclass
from typing import Deque, Dict


@dataclass(frozen=True)
class AttentionSnapshot:
    density: float
    velocity: float
    source_spread: float
    sentiment_bias: float


class SymbolAttentionProfile:
    """
    Minimal deterministic RSS attention tracker (v1).

    - Rolling window based on engine_time ticks
    - No decision authority
    - Observational only
    """

    def __init__(self, symbol: str, window_size: int = 300):
        self.symbol = symbol
        self.window_size = window_size

        self._events: Deque[Dict] = deque(maxlen=window_size)

    def ingest(self, event: Dict) -> None:
        """
        Expected event structure:
        {
            "engine_time": int,
            "source": str,
            "sentiment": float
        }
        """
        if not event:
            return

        self._events.append(event)

    def snapshot(self) -> AttentionSnapshot:
        if not self._events:
            return AttentionSnapshot(0.0, 0.0, 0.0, 0.0)

        count = len(self._events)
        unique_sources = len({e["source"] for e in self._events})
        sentiment_avg = sum(e["sentiment"] for e in self._events) / count

        density = count / self.window_size
        velocity = count / max(1, self.window_size)
        source_spread = unique_sources / count

        return AttentionSnapshot(
            density=density,
            velocity=velocity,
            source_spread=source_spread,
            sentiment_bias=sentiment_avg,
        )
