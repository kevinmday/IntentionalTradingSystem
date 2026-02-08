"""
Phase-1 canonical defaults for MarketState construction.

These values represent a clean, non-edge-case state
that should PASS the Phase-1 decision kernel.
"""

PHASE1_DEFAULTS = {
    # --- Structural (REQUIRED) ---
    "domain": "TEST",  # Phase-6 structural default

    # --- Core intention metrics ---
    "ucip": 0.75,
    "fils": 0.80,
    "ttcf": 0.10,

    # --- Narrative context (Phase-1 safe) ---
    "narrative": None,

    # --- Optional / contextual ---
    "fractal_levels": None,
    "symbol": "TEST",
    "data_source": "phase1_smoke",
    "engine_id": "TEST_ENGINE",
    "timestamp_utc": "2026-02-05T00:00:00Z",
}