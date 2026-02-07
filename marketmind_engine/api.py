from datetime import datetime
from typing import Optional, List
import os
from dataclasses import asdict

from marketmind_engine.core.clock import ENGINE_CLOCK
from marketmind_engine.data.registry import get_provider

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


# =========================
# Metrics
# =========================

def get_metrics() -> dict:
    """
    Engine-owned metrics.
    Flask must not compute metrics directly.
    """
    clock = ENGINE_CLOCK.now()
    provider = get_provider()

    return {
        **clock,

        # Legacy-safe observation timestamp
        "timestamp": datetime.utcnow().isoformat(),

        # Stub metrics (until live wiring)
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


# =========================
# Analysis
# =========================

def analyze_symbol(symbol: str, context: Optional[dict] = None) -> dict:
    """
    Analyze a single symbol.
    """
    clock = ENGINE_CLOCK.now()
    provider = get_provider()

    data = provider.get_symbol_data(symbol, context)

    return {
        **clock,
        "symbol": symbol.upper(),

        # Observation timestamp (external-facing)
        "timestamp": datetime.utcnow().isoformat(),

        # Provider-supplied numeric data
        **data,

        "engine": "marketmind_engine",
        "mode": "stub",
        "data_source": provider.name,
    }


def analyze_batch(symbols: List[str], context: Optional[dict] = None) -> dict:
    """
    Analyze multiple symbols.

    IMPORTANT:
    One engine tick per batch (not per symbol).
    """
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


# =========================
# Phase-6A — Read-Only Candidates
# =========================

def get_candidates() -> list[dict]:
    """
    Read-only access to Phase-6A trade candidates.

    This function exposes engine-truth candidates without
    computing, filtering, ranking, sizing, or executing.
    """
    clock = ENGINE_CLOCK.now()

    # NOTE:
    # This assumes evaluated assets already exist in engine state.
    # This function MUST remain read-only.
    evaluated_assets = getattr(get_provider(), "get_evaluated_assets", lambda: [])()

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


# =========================
# Decision + Policy
# =========================

def decide(signal: dict) -> dict:
    """
    Convert an analysis signal into a decision,
    then interpret it through the PolicyEngine.
    """
    clock = ENGINE_CLOCK.now()

    # --------------------------------------------------
    # Stub DecisionResult (rule logic wired later)
    # --------------------------------------------------
    decision_result = DecisionResult(
        rule_results=[],
        metadata={
            "note": "decision logic not implemented"
        }
    )

    # --------------------------------------------------
    # Policy evaluation
    # --------------------------------------------------
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


# =========================
# Health
# =========================

def health() -> dict:
    """
    Engine health check.
    """
    clock = ENGINE_CLOCK.now()
    provider = get_provider()

    return {
        **clock,
        "status": "ok",
        "engine": "marketmind_engine",
        "mode": "stub",
        "data_source": provider.name,
    }