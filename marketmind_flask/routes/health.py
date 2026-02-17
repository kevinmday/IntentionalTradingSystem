# marketmind_flask/routes/health.py

from flask import Blueprint, jsonify

health_bp = Blueprint("health", __name__)


@health_bp.route("/health", methods=["GET"])
def health():
    """
    Service-level health check.
    Does NOT call engine.
    Does NOT call adapters.
    Confirms Flask layer is alive.
    """
    return jsonify({
        "status": "ok",
        "service": "marketmind_flask"
    }), 200
