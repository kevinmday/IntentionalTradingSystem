from flask import Blueprint, jsonify
from marketmind_flask.adapters.engine_adapter import health_adapter

bp = Blueprint("health", __name__)

@bp.route("/health", methods=["GET"])
def health():
    result = health_adapter()
    return jsonify(result)
