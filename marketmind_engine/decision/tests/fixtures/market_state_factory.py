"""
Factory for constructing MarketState objects for Phase-1 tests.

This is the ONLY place MarketState should be instantiated
inside the Phase-1 test harness.
"""

from marketmind_engine.decision.state import MarketState
from .phase1_defaults import PHASE1_DEFAULTS


def make_market_state(**overrides) -> MarketState:
    """
    Create a MarketState with Phase-1 defaults,
    allowing explicit overrides per test.
    """
    data = PHASE1_DEFAULTS.copy()
    data.update(overrides)

    return MarketState(
        domain=data["domain"],                 # ✅ REQUIRED
        ucip=data["ucip"],
        fils=data["fils"],
        ttcf=data["ttcf"],
        narrative=data.get("narrative"),
        fractal_levels=data.get("fractal_levels"),
        symbol=data.get("symbol"),
        data_source=data.get("data_source"),
        engine_id=data.get("engine_id"),
        timestamp_utc=data.get("timestamp_utc"),
    )