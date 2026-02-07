"""
TEMPORARY METRIC SHIM — PHASE 3

Purpose:
- Enable deterministic replay before full metric migration
- Populate MarketState with placeholder UCIP / FILS / TTCF

NOTES:
- This is NOT final metric logic
- This will be replaced by mined monolith logic
- Do not tune against live trading
"""

from typing import Optional, Tuple

from marketmind_engine.adapters.contracts import LiquidityContext


def derive_metrics_phase3_shim(
    liquidity_ctx: Optional[LiquidityContext],
) -> Tuple[float, float, float]:
    """
    Phase-3 replay-only metric shim.

    Returns deterministic placeholder values so that:
    - replay plumbing can be validated
    - decision rules can execute
    - no trading logic is implied

    MUST NOT be used for live trading.
    """
    ucip = 0.5 if liquidity_ctx and liquidity_ctx.participating else 0.0
    fils = ucip
    ttcf = 0.1

    return ucip, fils, ttcf