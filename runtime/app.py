from flask import Flask, jsonify
from marketmind_engine.orchestrator.intraday_orchestrator import (
    IntradayOrchestrator,
)

app = Flask(__name__)

# -------------------------------------------------
# Engine instance (process-scoped)
# -------------------------------------------------

orchestrator = IntradayOrchestrator()

# -------------------------------------------------
# Regime Endpoint
# -------------------------------------------------

@app.get("/regime")
def regime():
    """
    Returns current regime state.
    Deterministic single-cycle evaluation.
    """
    result = orchestrator.run_cycle()
    return jsonify(result)


# -------------------------------------------------
# Entrypoint
# -------------------------------------------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=False)
