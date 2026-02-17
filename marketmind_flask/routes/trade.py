from flask import Blueprint, request, jsonify, current_app
from marketmind_flask.adapters.tradier_adapter import TradierAdapter
from marketmind_flask.adapters.engine_adapter import EngineAdapter
from datetime import datetime
import os

trade_bp = Blueprint("trade", __name__)

# Hard safety cap during paper testing
MAX_TEST_POSITION_DOLLARS = 1000


@trade_bp.route("/trade", methods=["POST"])
def execute_trade():
    """
    Manual execution endpoint.
    Uses engine-recommended sizing.
    """

    data = request.get_json(silent=True) or {}
    symbol = data.get("symbol")

    if not symbol:
        return jsonify({"error": "symbol required"}), 400

    # 1️⃣ Re-query engine for latest candidate state
    try:
        engine = EngineAdapter()
        candidate = engine.get_candidate(symbol)
    except Exception as e:
        current_app.logger.exception("Engine failure during trade execution")
        return jsonify({"error": "engine failure", "details": str(e)}), 500

    if not candidate:
        return jsonify({"error": "candidate not found"}), 404

    if not candidate.get("eligible", False):
        return jsonify({"error": "candidate not eligible"}), 400

    recommended_qty = candidate.get("recommended_quantity")
    price = candidate.get("price")

    if not recommended_qty or not price:
        return jsonify({"error": "invalid sizing data"}), 400

    # 2️⃣ Apply hard safety cap (paper-only guardrail)
    max_qty = int(MAX_TEST_POSITION_DOLLARS / price)

    if max_qty <= 0:
        return jsonify({"error": "price exceeds safety cap"}), 400

    final_qty = min(int(recommended_qty), max_qty)

    if final_qty <= 0:
        return jsonify({"error": "final quantity invalid"}), 400

    # 3️⃣ Execute via Tradier
    account_id = os.getenv("TRADIER_ACCOUNT_ID")
    if not account_id:
        return jsonify({"error": "TRADIER_ACCOUNT_ID not set"}), 500

    try:
        broker = TradierAdapter()
        result = broker.place_market_order(
            account_id=account_id,
            symbol=symbol,
            side="buy",
            quantity=final_qty
        )
    except Exception as e:
        current_app.logger.exception("Broker execution failure")
        return jsonify({"error": "broker execution failed", "details": str(e)}), 500

    # 4️⃣ Structured receipt
    receipt = {
        "symbol": symbol,
        "requested_quantity": recommended_qty,
        "executed_quantity": final_qty,
        "engine_score": candidate.get("score"),
        "regime": candidate.get("regime"),
        "broker_response": result,
        "timestamp": datetime.utcnow().isoformat()
    }

    current_app.logger.info(
        f"TRADE_SUBMITTED symbol={symbol} qty={final_qty}"
    )

    return jsonify(receipt), 200