# marketmind_flask/routes/metrics.py

from flask import Blueprint, jsonify
from marketmind_flask.adapters.engine_adapter import metrics_adapter

bp = Blueprint("metrics", __name__)

@bp.route("/metrics", methods=["GET"])
def metrics():
    return jsonify(metrics_adapter())
