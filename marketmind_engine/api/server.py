from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

from marketmind_engine.runtime.build_engine import build_engine
from marketmind_engine.api.models import (
    StartResponse,
    StopResponse,
    EngineStatus,
    RunDecisionResult,
    EngineStateSnapshot,
)

from marketmind_engine.intelligence.propagation_engine import PropagationEngine

# ------------------------------------------------------------------
# Authoritative Engine Bootstrap
# ------------------------------------------------------------------

engine_controller = build_engine()

# IMPORTANT:
# Adjust these two lines ONLY if attribute names differ in your build_engine() stack.
provider = engine_controller.provider
rss_service = engine_controller.rss_service

propagation_engine = PropagationEngine(
    provider=provider,
    engine_controller=engine_controller,
    rss_service=rss_service,
)

# ------------------------------------------------------------------
# FastAPI App
# ------------------------------------------------------------------

app = FastAPI(title="MarketMind Engine API")


class RunRequest(BaseModel):
    symbol: Optional[str] = "TEST"


# ------------------------------------------------------------------
# Engine Controls
# ------------------------------------------------------------------

@app.post("/engine/start", response_model=StartResponse)
def start_engine():
    engine_controller.start()
    return {"status": "started"}


@app.post("/engine/stop", response_model=StopResponse)
def stop_engine():
    engine_controller.stop()
    return {"status": "stopped"}


@app.get("/engine/status", response_model=EngineStatus)
def engine_status():
    return {
        "running": engine_controller.is_running(),
        "regime": None,
        "engine_time": None,
        "last_cycle_timestamp": None,
    }


# ------------------------------------------------------------------
# ACTION ENDPOINT (Decision Only)
# ------------------------------------------------------------------

@app.post("/engine/run", response_model=RunDecisionResult)
def run_engine(req: RunRequest):

    if not engine_controller.is_running():
        return {
            "decision": "NO_ACTION",
            "engine_time": -1,
            "symbol": req.symbol,
            "reason": "Engine is not started.",
        }

    try:
        result = engine_controller.run_symbol_cycle(req.symbol)

        return {
            "decision": result.get("decision", "UNKNOWN"),
            "engine_time": result.get("engine_time", 0),
            "symbol": req.symbol,
            "reason": result.get("reason"),
        }

    except Exception as e:
        return {
            "decision": "ERROR",
            "engine_time": -1,
            "symbol": req.symbol,
            "reason": str(e),
        }


# ------------------------------------------------------------------
# TELEMETRY ENDPOINT (Full Engine State)
# ------------------------------------------------------------------

@app.get("/engine/state", response_model=EngineStateSnapshot)
def engine_state():

    last = engine_controller.get_last_result()

    if not last:
        return {
            "running": engine_controller.is_running(),
            "regime": {
                "timestamp": 0.0,
                "regime": "unknown",
                "execution": {},
                "composite_score": 0.0,
                "recovery_modifier": 1.0,
                "domain_modifier": 1.0,
            },
            "engine_time": 0,
            "last_cycle_timestamp": None,
        }

    regime_snapshot = last.get("regime", {})

    return {
        "running": engine_controller.is_running(),
        "regime": regime_snapshot,
        "engine_time": last.get("engine_time", 0),
        "last_cycle_timestamp": regime_snapshot.get("timestamp"),
    }


# ------------------------------------------------------------------
# PROPAGATION OBSERVATORY (NEW)
# ------------------------------------------------------------------

@app.get("/propagation_snapshot")
def propagation_snapshot():
    """
    Multi-layer propagation intelligence snapshot.
    Pure observer layer.
    No mutation.
    """
    return propagation_engine.snapshot()


# ------------------------------------------------------------------
# Raw Debug Snapshot
# ------------------------------------------------------------------

@app.get("/engine/last")
def last_result():
    return engine_controller.get_last_result()