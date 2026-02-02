"""
Engine Adapter
--------------
Thin delegation layer between Flask and marketmind_engine.

Rules:
- No Flask imports
- No logic
- No defaults
- No state
"""

# marketmind_flask/adapters/engine_adapter.py

from marketmind_engine.api import (
    get_metrics,
    analyze_symbol,
    analyze_batch,
    decide,
    health,
)


def metrics_adapter() -> dict:
    """
    Thin delegation to engine metrics.
    """
    return get_metrics()


def analyze_symbol_adapter(symbol: str, context: dict | None = None) -> dict:
    """
    Thin delegation to engine analyze_symbol.
    """
    return analyze_symbol(symbol=symbol, context=context)


def analyze_batch_adapter(symbols: list[str], context: dict | None = None) -> dict:
    """
    Thin delegation to engine analyze_batch.
    """
    return analyze_batch(symbols=symbols, context=context)


def decide_adapter(signal: dict) -> dict:
    """
    Thin delegation to engine decision logic.
    """
    return decide(signal)


def health_adapter() -> dict:
    """
    Thin delegation to engine health.
    """
    return health()
