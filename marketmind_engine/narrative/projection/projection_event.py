from dataclasses import dataclass


@dataclass(frozen=True)
class ProjectionEvent:
    """
    Deterministic projection event emitted by NarrativeAdapter.
    """

    symbol: str
    engine_time: int
    source: str
    sentiment: float
    weight: float
