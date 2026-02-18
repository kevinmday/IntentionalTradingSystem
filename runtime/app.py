import sys
import os
from pathlib import Path

# -----------------------------------------------------------------------------
# Ensure repository root is on PYTHONPATH
# -----------------------------------------------------------------------------

ENGINE_DIR = Path(__file__).resolve().parent.parent
if str(ENGINE_DIR) not in sys.path:
    sys.path.insert(0, str(ENGINE_DIR))

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
# Environment
# -----------------------------------------------------------------------------

MM_ENV = os.getenv("MM_ENV", "dev")

# -----------------------------------------------------------------------------
# Flask App
# -----------------------------------------------------------------------------

app = Flask(__name__, static_folder="static")

if MM_ENV == "dev":
    CORS(app)
else:
    CORS(app, resources={r"/regime*": {"origins": "https://yourdomain.com"}})

# -----------------------------------------------------------------------------
# Orchestrator Builders
# -----------------------------------------------------------------------------

def build_live_orchestrator():
    """
    Construct live-mode orchestrator.
    MacroSource owns collection.
    """
    live_source = LiveMacroSource()
    return IntradayOrchestrator(macro_source=live_source)


def build_injected_orchestrator(macro_inputs: dict):
    injected_source = InjectedMacroSource(macro_inputs)
    return IntradayOrchestrator(macro_source=injected_source)


# Global session-scoped orchestrator
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


@app.route("/regime/inject", methods=["POST"])
def inject_regime():

    global orchestrator

    payload = request.get_json(silent=True)

    if not payload or "macro_inputs" not in payload:
        return jsonify({"error": "Payload must include 'macro_inputs'"}), 400

    orchestrator = build_injected_orchestrator(payload["macro_inputs"])

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