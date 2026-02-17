# marketmind_flask/routes/analyze.py

from flask import Blueprint, jsonify, request
from marketmind_flask.adapters.engine_adapter import EngineAdapter

analyze_bp = Blueprint("analyze", __name__)


@analyze_bp.route("/analyze/<symbol>", methods=["GET"])
def analyze_symbol(symbol: str):
    """
    Analyze a single symbol.
    Thin Flask → adapter → engine delegation.
    """

    engine = EngineAdapter()
    candidate = engine.get_candidate(symbol)

    if not candidate:
        return jsonify({"error": "analysis failed"}), 500

    return jsonify(candidate), 200


@analyze_bp.route("/analyze/batch", methods=["POST"])
def analyze_batch():
    """
    Analyze multiple symbols.

    Expects JSON:
    {
        "symbols": ["AAPL", "MSFT", ...]
    }
    """

    payload = request.get_json(silent=True) or {}
    symbols = payload.get("symbols", [])

    if not isinstance(symbols, list):
        return jsonify({
            "error": "symbols must be a list",
            "received": type(symbols).__name__,
        }), 400

    engine = EngineAdapter()

    results = []
    for symbol in symbols:
        candidate = engine.get_candidate(symbol)
        results.append({
            "symbol": symbol,
            "result": candidate
        })

    return jsonify(results), 200