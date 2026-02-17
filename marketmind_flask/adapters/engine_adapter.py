"""
Engine Adapter

Pure deterministic bridge into marketmind_engine.
No Flask.
No broker.
No execution.
"""

from marketmind_engine.api import analyze_symbol  # adjust if needed


class EngineAdapter:
    """
    Deterministic wrapper around marketmind_engine.
    """

    def get_candidate(self, symbol: str):
        """
        Returns structured candidate dict for Flask layer.
        """

        result = analyze_symbol(symbol)

        if not result:
            return None

        return {
            "symbol": symbol,
            "eligible": result.get("eligible", False),
            "score": result.get("score"),
            "price": result.get("price"),
            "recommended_quantity": result.get("recommended_quantity"),
            "regime": result.get("regime"),
            "raw": result
        }