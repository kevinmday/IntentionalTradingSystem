# =========================================================
# MARKETMIND ENGINE API
# =========================================================

from fastapi import FastAPI
from dotenv import load_dotenv

# Load environment variables immediately
load_dotenv()

# FastAPI app must exist at module load time for uvicorn reload
app = FastAPI(title="MarketMind Engine API")

# =========================================================
# Standard Imports
# =========================================================

from datetime import datetime
from typing import Optional, List
import os
from dataclasses import asdict

from marketmind_engine.core.clock import ENGINE_CLOCK
from marketmind_engine.data.registry import get_provider
from marketmind_engine.intelligence.propagation_engine import PropagationEngine

# =========================================================
# Decision + Policy
# =========================================================

from marketmind_engine.decision.types import DecisionResult
from marketmind_engine.policy.policy_engine import PolicyEngine
from marketmind_engine.policy.policy_base import PolicyInput
from marketmind_engine.policy.policies.conservative import ConservativePolicy
from marketmind_engine.policy.policies.observation_only import ObservationOnlyPolicy
from marketmind_engine.policy.formatters.explanation import (
    format_policy_explanation
)

# =========================================================
# Candidate Generation
# =========================================================

from marketmind_engine.candidates.emitter import emit_candidates

# =========================================================
# Policy Engine
# =========================================================

_POLICY_MAP = {
    "conservative": ConservativePolicy,
    "observation": ObservationOnlyPolicy,
}

_POLICY_NAME = os.getenv("MARKETMIND_POLICY", "conservative").lower()
_POLICY_CLASS = _POLICY_MAP.get(_POLICY_NAME, ConservativePolicy)

_POLICY_ENGINE = PolicyEngine(
    policy=_POLICY_CLASS()
)

# =========================================================
# ENGINE FUNCTIONS
# =========================================================

def get_metrics() -> dict:

    clock = ENGINE_CLOCK.now()
    provider = get_provider()

    return {
        **clock,
        "timestamp": datetime.utcnow().isoformat(),
        "rss_events_processed": 53,
        "echo_assets_analyzed": 17,
        "trades_simulated": 9,
        "ttcf_exits_triggered": 6,
        "ucip_avg": 0.48,
        "fils_avg": 76,
        "trades_closed_profitably": 7,
        "trades_closed_unprofitably": 2,
        "engine": "marketmind_engine",
        "mode": "live",
        "data_source": provider.name,
    }


# =========================================================
# SYMBOL ANALYSIS
# =========================================================

def analyze_symbol(symbol: str, context: Optional[dict] = None) -> dict:

    clock = ENGINE_CLOCK.now()
    provider = get_provider()

    data = provider.get_symbol_data(symbol, context)

    return {
        **clock,
        "symbol": symbol.upper(),
        "timestamp": datetime.utcnow().isoformat(),
        **data,
        "engine": "marketmind_engine",
        "mode": "live",
        "data_source": provider.name,
    }


def analyze_batch(symbols: List[str], context: Optional[dict] = None) -> dict:

    clock = ENGINE_CLOCK.now()
    provider = get_provider()

    batch_data = provider.get_batch_data(symbols, context)

    results = [
        {
            **clock,
            "symbol": symbol.upper(),
            "timestamp": datetime.utcnow().isoformat(),
            **batch_data.get(symbol.upper(), {}),
            "engine": "marketmind_engine",
            "mode": "live",
            "data_source": provider.name,
        }
        for symbol in symbols
    ]

    return {
        **clock,
        "timestamp": datetime.utcnow().isoformat(),
        "count": len(results),
        "results": results,
        "engine": "marketmind_engine",
        "mode": "live",
        "data_source": provider.name,
    }


# =========================================================
# CANDIDATE GENERATION
# =========================================================

def get_candidates() -> list[dict]:

    clock = ENGINE_CLOCK.now()

    evaluated_assets = getattr(
        get_provider(),
        "get_evaluated_assets",
        lambda: []
    )()

    engine_context = {
        "engine_id": clock["engine_id"],
        "engine_time": clock["engine_time"],
        "engine_tick": clock["engine_tick"],
    }

    candidates = emit_candidates(
        engine_context=engine_context,
        evaluated_assets=evaluated_assets,
    )

    return [asdict(c) for c in candidates]


# =========================================================
# POLICY DECISION
# =========================================================

def decide(signal: dict) -> dict:

    clock = ENGINE_CLOCK.now()

    decision_result = DecisionResult(
        rule_results=[],
        metadata={"note": "decision logic not implemented"}
    )

    policy_input = PolicyInput(
        decision_result=decision_result,
        market_state=signal,
        engine_time=ENGINE_CLOCK.now(),
    )

    policy_result = _POLICY_ENGINE.evaluate(policy_input)
    policy_explanation = format_policy_explanation(policy_result)

    return {
        **clock,
        "timestamp": datetime.utcnow().isoformat(),
        "decision": decision_result.to_dict(),
        "policy": {
            "policy_selected": _POLICY_NAME,
            "action": policy_result.action.value,
            "confidence": policy_result.confidence,
            "triggered_rules": policy_result.triggered_rules,
            "gating_reasons": policy_result.gating_reasons,
            "policy_name": policy_result.policy_name,
            "explanation": policy_explanation,
        },
        "engine": "marketmind_engine",
        "mode": "live",
        "data_source": "engine",
    }


# =========================================================
# NEW STRUCTURAL PROPAGATION ENGINE
# =========================================================

def get_propagation_snapshot() -> dict:

    clock = ENGINE_CLOCK.now()
    provider = get_provider()

    # Temporary stub services until runtime wiring exists
    class _StubController:
        def get_open_positions(self):
            return []

    class _StubRSS:
        def get_evaluated_symbols(self):
            return []

    engine = PropagationEngine(
        provider=provider,
        engine_controller=_StubController(),
        rss_service=_StubRSS(),
    )

    snapshot = engine.snapshot()

    return {
        **clock,
        **snapshot,
        "engine": "marketmind_engine",
        "data_source": provider.name,
    }


# =========================================================
# HEALTH CHECK
# =========================================================

def health() -> dict:

    clock = ENGINE_CLOCK.now()
    provider = get_provider()

    return {
        **clock,
        "status": "ok",
        "engine": "marketmind_engine",
        "mode": "live",
        "data_source": provider.name,
    }


# =========================================================
# API ROUTES
# =========================================================

@app.get("/api/metrics")
def metrics():
    return get_metrics()


@app.get("/api/analyze/{symbol}")
def analyze(symbol: str):
    return analyze_symbol(symbol)


@app.get("/api/candidates")
def candidates():
    return get_candidates()


@app.post("/api/decide")
def decision(signal: dict):
    return decide(signal)


@app.get("/api/propagation_snapshot")
def propagation_snapshot():
    return get_propagation_snapshot()


@app.get("/api/health")
def engine_health():
    return health()