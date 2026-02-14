import sys
import os

# -----------------------------------------------------------------------------
# Ensure project root is on PYTHONPATH
# -----------------------------------------------------------------------------

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS

from marketmind_engine.orchestrator.intraday_orchestrator import (
    IntradayOrchestrator,
)
from marketmind_engine.regime.macro_sources.live_source import LiveMacroSource
from marketmind_engine.regime.macro_sources.injected_source import (
    InjectedMacroSource,
)

# -----------------------------------------------------------------------------
# Environment Detection
# -----------------------------------------------------------------------------

MM_ENV = os.getenv("MM_ENV", "dev")  # dev | prod

# -----------------------------------------------------------------------------
# Flask App
# -----------------------------------------------------------------------------

app = Flask(__name__, static_folder="static")

# -----------------------------------------------------------------------------
# CORS Configuration
# -----------------------------------------------------------------------------

if MM_ENV == "dev":
    CORS(
        app,
        resources={
            r"/regime*": {"origins": r"http://localhost:\d+"}
        },
    )
else:
    CORS(
        app,
        resources={
            r"/regime*": {"origins": "https://yourdomain.com"}
        },
    )

# -----------------------------------------------------------------------------
# Orchestrator Wiring (Phase 11.5)
# -----------------------------------------------------------------------------

def build_live_orchestrator():
    """
    Construct a fresh live-mode orchestrator.
    Deterministic clean state.
    """

    bootstrap = IntradayOrchestrator(macro_source=None)

    live_source = LiveMacroSource(
        bootstrap._collect_macro_inputs
    )

    return IntradayOrchestrator(
        macro_source=live_source,
    )


def build_injected_orchestrator(macro_inputs: dict):
    """
    Construct a fresh injected-mode orchestrator.
    """

    injected_source = InjectedMacroSource(macro_inputs)

    return IntradayOrchestrator(
        macro_source=injected_source,
    )


# Global orchestrator instance (session-scoped for now)
orchestrator = build_live_orchestrator()

# -----------------------------------------------------------------------------
# Routes
# -----------------------------------------------------------------------------

@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/regime")
def regime():
    snapshot = orchestrator.run_cycle()
    return jsonify(snapshot)


# -----------------------------------------------------------------------------
# Injection Endpoints (Phase 11.5)
# -----------------------------------------------------------------------------

@app.route("/regime/inject", methods=["POST"])
def inject_regime():

    global orchestrator

    payload = request.get_json(silent=True)

    if not payload or "macro_inputs" not in payload:
        return jsonify({
            "error": "Payload must include 'macro_inputs' dict"
        }), 400

    macro_inputs = payload["macro_inputs"]

    required_fields = [
        "drawdown_velocity",
        "liquidity_stress",
        "correlation_spike",
        "narrative_shock",
        "structural_confirmation",
    ]

    for field in required_fields:
        if field not in macro_inputs:
            return jsonify({
                "error": f"Missing required macro input field: {field}"
            }), 400

    # Build new injected orchestrator (clean state)
    orchestrator = build_injected_orchestrator(macro_inputs)

    snapshot = orchestrator.run_cycle()

    return jsonify({
        "injection_active": True,
        "snapshot": snapshot,
    })


@app.route("/regime/inject/disable", methods=["POST"])
def disable_injection():

    global orchestrator

    orchestrator = build_live_orchestrator()

    snapshot = orchestrator.run_cycle()

    return jsonify({
        "injection_active": False,
        "snapshot": snapshot,
    })


# -----------------------------------------------------------------------------
# Runtime
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    app.run(port=5001, debug=False)