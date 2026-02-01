"""
marketmind_engine API
---------------------
Public, stable interface for the MarketMind engine.

NOTE:
This is a contract-first stub.
Behavior will be wired in later.
"""

# marketmind_engine/api.py

from datetime import datetime

def get_metrics():
    """
    Engine-owned metrics (stub).
    Flask must not compute metrics directly.
    """
    return {
        "timestamp": datetime.utcnow().isoformat(),
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
    }


def analyze_symbol(symbol: str, context: dict | None = None) -> dict:
    raise NotImplementedError("analyze_symbol not implemented yet")


def analyze_batch(symbols: list[str], context: dict | None = None) -> dict:
    raise NotImplementedError("analyze_batch not implemented yet")


def decide(signal: dict) -> dict:
    raise NotImplementedError("decide not implemented yet")


def health() -> dict:
    return {
        "status": "ok",
        "engine": "marketmind_engine",
        "mode": "stub",
    }
