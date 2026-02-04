"""
marketmind_engine API
---------------------
Public, stable interface for the MarketMind engine.

NOTE:
This is a contract-first implementation.
Behavior is wired incrementally.
"""

from datetime import datetime
from typing import Optional, List

from marketmind_engine.core.clock import ENGINE_CLOCK
from marketmind_engine.data.registry import get_provider

# Decision + Policy
from marketmind_engine.decision.results import DecisionResult
from marketmind_engine.policy.policy_engine import PolicyEngine
from marketmind_engine.policy.policy_base import PolicyInput
from marketmind_engine.policy.policies.observation_only import ObservationOnlyPolicy


# =========================
# Policy Engine (static for now)
# =========================

_POLICY_ENGINE = PolicyEngine(
    policy=ObservationOnlyPolicy()
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

    return {
        **clock,
        "timestamp": datetime.utcnow().isoformat(),

        "decision": decision_result.to_dict(),

        "policy": {
            "action": policy_result.action.value,
            "confidence": policy_result.confidence,
            "triggered_rules": policy_result.triggered_rules,
            "gating_reasons": policy_result.gating_reasons,
            "policy_name": policy_result.policy_name,
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
