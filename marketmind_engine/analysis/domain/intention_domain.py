"""
IntentionDomain (Phase-4C)

Represents a coherent public-intention market domain
(e.g., Defense AI, Energy Security, Antitrust).
"""

from dataclasses import dataclass
from typing import List, Optional


@dataclass(frozen=True)
class IntentionDomain:
    name: str
    fils: float
    ucip: Optional[float] = None
    ttcf: Optional[float] = None

    narratives: Optional[List[str]] = None
    confidence: Optional[float] = None