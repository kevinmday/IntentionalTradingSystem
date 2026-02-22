from dataclasses import dataclass
from typing import Optional

from marketmind_engine.adapters.contracts import NarrativeContext


@dataclass(frozen=True)
class NarrativeScores:
    fils: float
    ucip: float
    ttcf: float
    explanation: str


class NarrativeScoringEngine:
    """
    Deterministic scoring engine mapping NarrativeContext
    into FILS / UCIP / TTCF.

    No randomness.
    No hidden state.
    Replay-safe.
    """

    def score(self, ctx: Optional[NarrativeContext]) -> Optional[NarrativeScores]:
        if ctx is None or not ctx.accelerating:
            return None

        # --- Acceleration strength ---
        prior = max(ctx.mentions_prior, 1)
        current = ctx.mentions_current

        acceleration_ratio = current / prior

        # Normalize acceleration (cap at 3x)
        accel_strength = min(acceleration_ratio / 3.0, 1.0)

        # --- Source diversity factor ---
        source_factor = min(ctx.source_count / 5.0, 1.0)

        # --- FILS ---
        fils = 0.5 + 0.4 * accel_strength + 0.1 * source_factor
        fils = min(max(fils, 0.0), 1.0)

        # --- UCIP ---
        ucip = 0.4 + 0.5 * accel_strength + 0.1 * source_factor
        ucip = min(max(ucip, 0.0), 1.0)

        # --- TTCF (inverse stability proxy) ---
        ttcf = 0.3 - 0.2 * accel_strength - 0.1 * source_factor
        ttcf = min(max(ttcf, 0.01), 0.5)

        explanation = (
            f"accel={acceleration_ratio:.2f}, "
            f"sources={ctx.source_count}, "
            f"strength={accel_strength:.2f}"
        )

        return NarrativeScores(
            fils=round(fils, 3),
            ucip=round(ucip, 3),
            ttcf=round(ttcf, 3),
            explanation=explanation,
        )