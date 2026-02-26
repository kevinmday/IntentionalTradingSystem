from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional, Dict, Any
import inspect

from marketmind_engine.runtime.build_engine import build_engine
from marketmind_engine.execution.execution_input import ExecutionInput


# ------------------------------------------------------------------
# Authoritative Engine Bootstrap
# ------------------------------------------------------------------

engine_controller = build_engine()


# ------------------------------------------------------------------
# FastAPI App
# ------------------------------------------------------------------

app = FastAPI(title="MarketMind Engine API")


class RunRequest(BaseModel):
    symbol: Optional[str] = None


# ------------------------------------------------------------------
# Engine Controls
# ------------------------------------------------------------------

@app.post("/engine/start")
def start_engine():
    engine_controller.start()
    return {"status": "started"}


@app.post("/engine/stop")
def stop_engine():
    engine_controller.stop()
    return {"status": "stopped"}


@app.get("/engine/status")
def engine_status():
    return {
        "running": engine_controller.is_running(),
    }


# ------------------------------------------------------------------
# Manual Cycle Trigger
# ------------------------------------------------------------------

@app.post("/engine/run")
def run_engine(req: RunRequest):

    if not engine_controller.is_running():
        return {"error": "Engine is not started."}

    try:
        # Inspect ExecutionInput signature dynamically
        sig = inspect.signature(ExecutionInput)
        params = sig.parameters

        # Build kwargs dynamically based on actual constructor
        kwargs: Dict[str, Any] = {}

        if "symbol" in params:
            kwargs["symbol"] = req.symbol or "TEST"

        # Add additional safe defaults if needed
        if "timestamp" in params:
            kwargs["timestamp"] = None

        execution_input = ExecutionInput(**kwargs)

        result = engine_controller.run_once(execution_input)

        return {
            "success": True,
            "input": kwargs,
            "result": result,
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


# ------------------------------------------------------------------
# Last Result Snapshot
# ------------------------------------------------------------------

@app.get("/engine/last")
def last_result():
    return engine_controller.get_last_result()