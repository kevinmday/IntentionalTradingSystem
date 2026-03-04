from pydantic import BaseModel
from typing import Optional, Dict, Any


# ------------------------------------------------------------------
# Engine Control Responses
# ------------------------------------------------------------------

class StartResponse(BaseModel):
    status: str


class StopResponse(BaseModel):
    status: str


# ------------------------------------------------------------------
# Lightweight Engine Status (simple health check)
# ------------------------------------------------------------------

class EngineStatus(BaseModel):
    running: bool
    regime: Optional[str] = None
    engine_time: Optional[int] = None
    last_cycle_timestamp: Optional[float] = None


# ------------------------------------------------------------------
# Action Result (Decision Only)
# ------------------------------------------------------------------

class RunDecisionResult(BaseModel):
    decision: str
    engine_time: int
    symbol: Optional[str] = None
    reason: Optional[str] = None


# ------------------------------------------------------------------
# Full Regime Snapshot (Authoritative Runtime State)
# ------------------------------------------------------------------

class RegimeSnapshot(BaseModel):
    timestamp: float
    regime: str
    execution: Dict[str, Any]
    composite_score: float
    recovery_modifier: float
    domain_modifier: float


# ------------------------------------------------------------------
# Engine Telemetry State (For UI / Dashboard)
# ------------------------------------------------------------------

class EngineStateSnapshot(BaseModel):
    running: bool
    regime: RegimeSnapshot
    engine_time: int
    last_cycle_timestamp: Optional[float] = None
