from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class NarrativeContext:
    accelerating: bool
    source_count: int
    window: str
    notes: Optional[str] = None

    # Phase-1 compatibility
    mentions_current: int = 0
    mentions_prior: int = 0
    mentions_previous: int = 0