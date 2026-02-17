# marketmind_flask/routes/metrics.py

from flask import Blueprint, jsonify, request
from marketmind_flask.adapters.engine_adapter import EngineAdapter

metrics_bp = Blueprint("metrics", __name__)


@metrics_bp.route("/metrics/<symbol>", methods=["GET"])
def metrics(symbol: str):
    """
    Returns key engine metrics for a symbol.
    Thin Flask → adapter → engine delegation.
    """

    engine = EngineAdapter()
    candidate = engine.get_candidate(symbol)

    if not candidate:
        return jsonify({"error": "analysis failed"}), 500

    return jsonify({
        "symbol": candidate.get("symbol"),
        "score": candidate.get("score"),
        "regime": candidate.get("regime"),
        "eligible": candidate.get("eligible"),
        "price": candidate.get("price"),
    }), 200