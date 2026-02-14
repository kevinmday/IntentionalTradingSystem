import sys
import os

# Ensure project root is on PYTHONPATH
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from marketmind_engine.orchestrator.intraday_orchestrator import IntradayOrchestrator

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
    # Allow any localhost port (Vite auto-port safe)
    CORS(
        app,
        resources={r"/regime": {"origins": r"http://localhost:\d+"}}
    )
else:
    # 🔒 Lock this to your production domain later
    CORS(
        app,
        resources={r"/regime": {"origins": "https://yourdomain.com"}}
    )

# -----------------------------------------------------------------------------
# Orchestrator
# -----------------------------------------------------------------------------

orchestrator = IntradayOrchestrator()

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
# Runtime
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    app.run(port=5001, debug=False)