"""
Phase-6A Golden Test

This test freezes the candidate materialization contract and guarantees
deterministic, read-only emission behavior.

If this test breaks in the future, the engine output contract has changed.
That is a breaking change.
"""

from datetime import datetime, timezone

from marketmind_engine.candidates.contract import TradeCandidate
from marketmind_engine.candidates.emitter import emit_candidates


def test_phase6a_candidate_emission_is_deterministic():
    """
    GIVEN a fully-evaluated engine state
    WHEN candidates are emitted
    THEN the output is deterministic, complete, and unfiltered
    """

    # --- Fake engine clock snapshot (authoritative) ---
    engine_context = {
        "engine_id": "TEST_ENGINE",
        "engine_time": datetime(2026, 2, 7, 15, 0, tzinfo=timezone.utc),
        "engine_tick": 42,
    }

    # --- Fake evaluated market state ---
    evaluated_assets = [
        {
            "symbol": "AAA",
            "domain": "TEST_DOMAIN",
            "metrics": {"fils": 72.5, "ucip": 0.81, "ttcf": 0.12},
            "eligibility": (True, "Passed all eligibility checks"),
            "market_confirmation": (True, "Sufficient liquidity"),
            "decision": "ALLOW",
            "narrative": "Narrative pressure supports upward expression.",
        },
        {
            "symbol": "BBB",
            "domain": "TEST_DOMAIN",
            "metrics": {"fils": 41.0, "ucip": 0.55, "ttcf": 0.31},
            "eligibility": (False, "FILS below minimum"),
            "market_confirmation": (False, "Volatility exceeds tolerance"),
            "decision": "NO_ACTION",
            "narrative": "Narrative signal present but incoherent.",
        },
    ]

    # --- Emit candidates ---
    candidates = emit_candidates(
        engine_context=engine_context,
        evaluated_assets=evaluated_assets,
    )

    # --- Structural assertions ---
    assert isinstance(candidates, list)
    assert len(candidates) == 2

    for c in candidates:
        assert isinstance(c, TradeCandidate)

    # --- Deterministic ordering (symbol-lexical) ---
    assert candidates[0].symbol == "AAA"
    assert candidates[1].symbol == "BBB"

    # --- Field-level assertions (first candidate) ---
    c0 = candidates[0]

    assert c0.engine_id == "TEST_ENGINE"
    assert c0.engine_tick == 42
    assert c0.fils == 72.5
    assert c0.ucip == 0.81
    assert c0.ttcf == 0.12
    assert c0.eligibility_status is True
    assert c0.market_confirmation_status is True
    assert c0.decision == "ALLOW"

    # --- Field-level assertions (second candidate) ---
    c1 = candidates[1]

    assert c1.eligibility_status is False
    assert c1.market_confirmation_status is False
    assert c1.decision == "NO_ACTION"

    # --- Invariant: NO filtering ---
    symbols = {c.symbol for c in candidates}
    assert symbols == {"AAA", "BBB"}