"""
Market confirmation gates (Phase-5C).

Quantitative checks that confirm whether the market
can reflect intention already observed.

IMPORTANT:
- Quant NEVER creates signals here
- Quant NEVER overrides narrative
- This module only answers: "Can the market express it?"
"""

from dataclasses import dataclass
from marketmind_engine.decision.state import MarketState


@dataclass(frozen=True)
class ConfirmationResult:
    confirmed: bool
    reason: str


# --------------------------------------------------
# Capacity thresholds (policy, not math)
# --------------------------------------------------

MIN_LIQUIDITY = 0.30        # Market participation floor
MAX_VOLATILITY = 0.70       # Chaos ceiling
MIN_RESPONSIVENESS = 0.25   # Ability to move when pushed


def confirm_market_capacity(state: MarketState) -> ConfirmationResult:
    """
    Confirm that the market has sufficient structural
    capacity to reflect observed intention.

    This function is PERMISSION-ONLY.
    It does not generate or suppress intent.
    """

    # -------------------------------
    # Liquidity gate
    # -------------------------------
    if state.liquidity is not None:
        if state.liquidity < MIN_LIQUIDITY:
            return ConfirmationResult(
                confirmed=False,
                reason="Insufficient liquidity",
            )

    # -------------------------------
    # Volatility gate
    # -------------------------------
    if state.volatility is not None:
        if state.volatility > MAX_VOLATILITY:
            return ConfirmationResult(
                confirmed=False,
                reason="Excessive volatility",
            )

    # -------------------------------
    # Responsiveness gate
    # -------------------------------
    if state.responsiveness is not None:
        if state.responsiveness < MIN_RESPONSIVENESS:
            return ConfirmationResult(
                confirmed=False,
                reason="Market unresponsive",
            )

    # -------------------------------
    # Capacity confirmed
    # -------------------------------
    return ConfirmationResult(
        confirmed=True,
        reason="Market capacity confirmed",
    )