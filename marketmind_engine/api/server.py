from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import threading
import time

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

engine_loop_thread = None
engine_loop_running = False


# ------------------------------------------------------------------
# SAFE ATTRIBUTE DISCOVERY
# ------------------------------------------------------------------

provider = getattr(engine_controller, "provider", None)
rss_service = getattr(engine_controller, "rss_service", None)

propagation_engine = PropagationEngine(
    provider=provider,
    engine_controller=engine_controller,
    rss_service=rss_service,
)


# ------------------------------------------------------------------
# FastAPI App
# ------------------------------------------------------------------

app = FastAPI(title="MarketMind Engine API")


# ------------------------------------------------------------------
# CORS CONFIGURATION (REQUIRED FOR UI POLLING)
# ------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RunRequest(BaseModel):
    symbol: Optional[str] = None


# ------------------------------------------------------------------
# ENGINE LOOP
# ------------------------------------------------------------------

def engine_loop():

    global engine_loop_running

    while engine_loop_running:

        try:
            if engine_controller.is_running():
                engine_controller.run_symbol_cycle("TEST")

        except Exception as e:
            print("Engine loop error:", e)

        time.sleep(2)


# ------------------------------------------------------------------
# ENGINE CONTROL ENDPOINTS
# ------------------------------------------------------------------

@app.post("/api/engine/start", response_model=StartResponse)
def start_engine():

    global engine_loop_thread
    global engine_loop_running

    engine_controller.start()

    if not engine_loop_running:

        engine_loop_running = True

        engine_loop_thread = threading.Thread(
            target=engine_loop,
            daemon=True
        )

        engine_loop_thread.start()

    return {"status": "started"}


@app.post("/api/engine/stop", response_model=StopResponse)
def stop_engine():

    global engine_loop_running

    engine_controller.stop()
    engine_loop_running = False

    return {"status": "stopped"}


@app.get("/api/engine/status", response_model=EngineStatus)
def engine_status():

    last = engine_controller.get_last_result()

    regime_name = None
    engine_time = None
    timestamp = None

    if last:

        engine_time = last.get("engine_time")

        regime_snapshot = last.get("regime")

        if isinstance(regime_snapshot, dict):

            regime_name = regime_snapshot.get("regime")
            timestamp = regime_snapshot.get("timestamp")

    return {
        "running": engine_controller.is_running(),
        "regime": regime_name,
        "engine_time": engine_time,
        "last_cycle_timestamp": timestamp,
    }


# ------------------------------------------------------------------
# ACTION ENDPOINT
# ------------------------------------------------------------------

@app.post("/api/engine/run", response_model=RunDecisionResult)
def run_engine(req: Optional[RunRequest] = None):

    symbol = "TEST"

    if req and req.symbol:
        symbol = req.symbol

    if not engine_controller.is_running():
        return {
            "decision": "NO_ACTION",
            "engine_time": -1,
            "symbol": symbol,
            "reason": "Engine is not started.",
        }

    try:

        result = engine_controller.run_symbol_cycle(symbol)

        return {
            "decision": result.get("decision", "UNKNOWN"),
            "engine_time": result.get("engine_time", 0),
            "symbol": symbol,
            "reason": result.get("reason"),
        }

    except Exception as e:

        return {
            "decision": "ERROR",
            "engine_time": -1,
            "symbol": symbol,
            "reason": str(e),
        }


# ------------------------------------------------------------------
# ENGINE TELEMETRY
# ------------------------------------------------------------------

@app.get("/api/engine/state", response_model=EngineStateSnapshot)
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

            "regime_name": "unknown",
            "flatten_triggered": False,
            "block_new_entries": False
        }

    regime_snapshot = last.get("regime")

    if not isinstance(regime_snapshot, dict):
        regime_snapshot = {
            "timestamp": 0.0,
            "regime": "unknown",
            "execution": {},
            "composite_score": 0.0,
            "recovery_modifier": 1.0,
            "domain_modifier": 1.0,
        }

    regime_name = regime_snapshot.get("regime", "unknown")

    execution = regime_snapshot.get("execution", {})

    allow_entries = execution.get("allow_entries", True)

    flatten_triggered = not allow_entries
    block_new_entries = not allow_entries

    return {
        "running": engine_controller.is_running(),
        "regime": regime_snapshot,
        "engine_time": last.get("engine_time", 0),
        "last_cycle_timestamp": regime_snapshot.get("timestamp"),

        "regime_name": regime_name,
        "flatten_triggered": flatten_triggered,
        "block_new_entries": block_new_entries
    }


# ------------------------------------------------------------------
# PROPAGATION OBSERVATORY
# ------------------------------------------------------------------

@app.get("/api/propagation_snapshot")
def propagation_snapshot():

    try:
        return propagation_engine.snapshot()

    except Exception:
        return {"status": "propagation_unavailable"}


# ------------------------------------------------------------------
# NARRATIVE RADAR
# ------------------------------------------------------------------

@app.get("/api/narrative_radar")
def narrative_radar():

    return {
        "updated": "now",
        "domains": [
            {"domain": "ai-bio", "score": 72},
            {"domain": "defense", "score": 54},
            {"domain": "energy", "score": 33},
            {"domain": "macro", "score": 21},
        ],
        "symbols": [
            {"symbol": "NVDA", "mentions": 12, "momentum": 1.42},
            {"symbol": "PLTR", "mentions": 7, "momentum": 1.18},
            {"symbol": "SMCI", "mentions": 5, "momentum": 1.09},
        ],
    }


# ------------------------------------------------------------------
# DEBUG SNAPSHOT
# ------------------------------------------------------------------

@app.get("/api/engine/last")
def last_result():

    return engine_controller.get_last_result()