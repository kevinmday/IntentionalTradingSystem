# marketmind_flask/routes/analyze.py

from flask import Blueprint, jsonify, request

from marketmind_flask.adapters.engine_adapter import (
    analyze_symbol_adapter,
    analyze_batch_adapter,
)

bp = Blueprint("analyze", __name__)


@bp.route("/analyze/<symbol>", methods=["GET"])
def analyze_symbol(symbol: str):
    """
    Analyze a single symbol.
    Thin Flask → adapter → engine delegation.
    """
    result = analyze_symbol_adapter(symbol=symbol)
    return jsonify(result)


@bp.route("/analyze/batch", methods=["POST"])
def analyze_batch():
    """
    Analyze multiple symbols.

    Expects JSON:
    {
        "symbols": ["AAPL", "MSFT", ...],
        "context": {...}   # optional
    }
    """
    payload = request.get_json(silent=True) or {}

    symbols = payload.get("symbols", [])
    context = payload.get("context")

    if not isinstance(symbols, list):
        return jsonify({
            "error": "symbols must be a list",
            "received": type(symbols).__name__,
        }), 400

    result = analyze_batch_adapter(symbols=symbols, context=context)
    return jsonify(result)
