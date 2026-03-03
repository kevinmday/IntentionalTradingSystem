from datetime import datetime
from typing import Optional, List
import os
import random
from dataclasses import asdict

from fastapi import FastAPI

from marketmind_engine.core.clock import ENGINE_CLOCK
from marketmind_engine.data.registry import get_provider

# =========================================================
# FastAPI App
# =========================================================

app = FastAPI(title="MarketMind Engine API")

# =========================
# Decision + Policy
# =========================

from marketmind_engine.decision.types import DecisionResult
from marketmind_engine.policy.policy_engine import PolicyEngine
from marketmind_engine.policy.policy_base import PolicyInput
from marketmind_engine.policy.policies.conservative import ConservativePolicy
from marketmind_engine.policy.policies.observation_only import ObservationOnlyPolicy
from marketmind_engine.policy.formatters.explanation import (
    format_policy_explanation
)

# =========================
# Phase-6A Candidates
# =========================

from marketmind_engine.candidates.emitter import emit_candidates

# =========================
# Policy Engine (static, selectable)
# =========================

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
# Engine Functions
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
        "mode": "stub",
        "data_source": provider.name,
    }


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
        "mode": "stub",
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
            "mode": "stub",
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
        "mode": "stub",
        "data_source": provider.name,
    }


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
        "mode": "stub",
        "data_source": "engine",
    }


def get_propagation_snapshot() -> dict:
    """
    Read-only propagation telemetry stub.
    No execution logic.
    No capital state.
    Pure instrumentation.
    """
    clock = ENGINE_CLOCK.now()

    return {
        **clock,
        "timestamp": datetime.utcnow().isoformat(),
        "sector_avg": round(random.uniform(-1.5, 3.5), 2),
        "prime_avg": round(random.uniform(-1.0, 4.0), 2),
        "breadth": random.randint(3, 12),
        "etf_confirmation": random.choice([True, False]),
        "pullback_depth": round(random.uniform(-1.2, 0), 2),
        "volume_delta": round(random.uniform(-10, 25), 2),
        "engine": "marketmind_engine",
        "mode": "propagation_stub",
        "data_source": "mock",
    }


def health() -> dict:
    clock = ENGINE_CLOCK.now()
    provider = get_provider()

    return {
        **clock,
        "status": "ok",
        "engine": "marketmind_engine",
        "mode": "stub",
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