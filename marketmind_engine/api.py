"""
marketmind_engine API
---------------------
Public, stable interface for the MarketMind engine.

NOTE:
This is a contract-first stub.
Behavior will be wired in later.
"""

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
