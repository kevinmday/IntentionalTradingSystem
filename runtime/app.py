from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from marketmind_engine.orchestrator.intraday_orchestrator import IntradayOrchestrator

app = Flask(__name__, static_folder="static")

# Controlled CORS — allow React dev server only for /regime
CORS(
    app,
    resources={r"/regime": {"origins": "http://localhost:5173"}}
)

orchestrator = IntradayOrchestrator()


@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/regime")
def regime():
    snapshot = orchestrator.run_cycle()
    return jsonify(snapshot)


if __name__ == "__main__":
    app.run(port=5001, debug=False)