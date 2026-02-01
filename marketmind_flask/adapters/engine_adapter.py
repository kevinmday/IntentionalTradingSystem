"""
Engine Adapter
---------------
Thin delegation layer between Flask and marketmind_engine.

Rules:
- No Flask imports
- No logic
- No defaults
- No state
"""

from marketmind_engine.api import (
    analyze_symbol,
    analyze_batch,
    decide,
    health,
)


def analyze_symbol_adapter(symbol: str, context: dict | None = None):
    return analyze_symbol(symbol=symbol, context=context)


def analyze_batch_adapter(symbols: list[str], context: dict | None = None):
    return analyze_batch(symbols=symbols, context=context)


def decide_adapter(signal: dict):
    return decide(signal=signal)


def health_adapter():
    return health()
