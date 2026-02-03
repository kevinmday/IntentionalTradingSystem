"""
marketmind_engine API
---------------------
Public, stable interface for the MarketMind engine.

NOTE:
This is a contract-first implementation.
Behavior will be wired in incrementally.
"""

from datetime import datetime
from typing import Optional, List

from marketmind_engine.core.clock import ENGINE_CLOCK
from marketmind_engine.data.registry import get_provider


# =========================
# Metrics
# =========================

def get_metrics() -> dict:
    """
    Engine-owned metrics.
    Flask must not compute metrics directly.
    """
    clock = ENGINE_CLOCK.now()
    provider = get_provider()

    return {
        **clock,

        # Legacy-safe observation timestamp
        "timestamp": datetime.utcnow().isoformat(),

        # Stub metrics (until live wiring)
        "rss_events_processed": 53,
        "echo_assets_analyzed": 17,
        "trades_simulated": 9,
        "ttcf_exits_triggered": 6,
        "ucip_avg": 0.48,
        "fils_avg": 76,
        "trades_closed_profitably": 7,
        "trades_closed_unprofitably": 2,

        "engine": "marketmind_engine",
        "mode": "stub",
        "data_source": provider.name,
    }


# =========================
# Analysis
# =========================

def analyze_symbol(symbol: str, context: Optional[dict] = None) -> dict:
    """
    Analyze a single symbol.
    """
    clock = ENGINE_CLOCK.now()
    provider = get_provider()

    data = provider.get_symbol_data(symbol, context)

    return {
        **clock,

        "symbol": symbol.upper(),

        # Observation timestamp (external-facing)
        "timestamp": datetime.utcnow().isoformat(),

        # Provider-supplied numeric data
        **data,

        "engine": "marketmind_engine",
        "mode": "stub",
        "data_source": provider.name,
    }


def analyze_batch(symbols: List[str], context: Optional[dict] = None) -> dict:
    """
    Analyze multiple symbols.

    IMPORTANT:
    One engine tick per batch (not per symbol).
    """
    clock = ENGINE_CLOCK.now()
    provider = get_provider()

    batch_data = provider.get_batch_data(symbols, context)

    results = [
        {
            **clock,
            "symbol": symbol.upper(),
            "timestamp": datetime.utcnow().isoformat(),
            **batch_data.get(symbol.upper(), {}),
            "engine": "marketmind_engine",
            "mode": "stub",
            "data_source": provider.name,
        }
        for symbol in symbols
    ]

    return {
        **clock,
        "timestamp": datetime.utcnow().isoformat(),
        "count": len(results),
        "results": results,
        "engine": "marketmind_engine",
        "mode": "stub",
        "data_source": provider.name,
    }


# =========================
# Decision
# =========================

def decide(signal: dict) -> dict:
    """
    Convert an analysis signal into a decision.
    """
    clock = ENGINE_CLOCK.now()

    return {
        **clock,
        "timestamp": datetime.utcnow().isoformat(),
        "decision": "NO_ACTION",
        "reason": "decision logic not implemented",
        "input_signal": signal,
        "engine": "marketmind_engine",
        "mode": "stub",
        "data_source": "engine",
    }


# =========================
# Health
# =========================

def health() -> dict:
    """
    Engine health check.
    """
    clock = ENGINE_CLOCK.now()
    provider = get_provider()

    return {
        **clock,
        "status": "ok",
        "engine": "marketmind_engine",
        "mode": "stub",
        "data_source": provider.name,
    }
