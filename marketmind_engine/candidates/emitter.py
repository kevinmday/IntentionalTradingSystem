"""
Phase-6A Candidate Emitter

Assembles TradeCandidate objects from evaluated engine state.
This module performs no calculations, filtering, or ranking.
"""

from typing import List

from marketmind_engine.candidates.contract import TradeCandidate


def emit_candidates(*, engine_context: dict, evaluated_assets: list) -> List[TradeCandidate]:
    """
    Deterministically assemble TradeCandidate objects from evaluated assets.

    Parameters
    ----------
    engine_context : dict
        Authoritative engine clock snapshot. Must contain:
        - engine_id
        - engine_time
        - engine_tick

    evaluated_assets : list
        List of evaluated asset dicts produced after decision evaluation.

    Returns
    -------
    List[TradeCandidate]
        Deterministic, unfiltered list of trade candidates.
    """

    # Enforce deterministic ordering (lexical by symbol)
    ordered_assets = sorted(evaluated_assets, key=lambda a: a["symbol"])

    candidates: List[TradeCandidate] = []

    for asset in ordered_assets:
        eligibility_status, eligibility_reason = asset["eligibility"]
        market_status, market_reason = asset["market_confirmation"]

        candidate = TradeCandidate(
            # Identity
            symbol=asset["symbol"],
            domain=asset["domain"],

            # Engine context
            engine_id=engine_context["engine_id"],
            engine_time=engine_context["engine_time"],
            engine_tick=engine_context["engine_tick"],

            # Intention metrics
            fils=asset["metrics"]["fils"],
            ucip=asset["metrics"]["ucip"],
            ttcf=asset["metrics"]["ttcf"],

            # Eligibility (observational)
            eligibility_status=eligibility_status,
            eligibility_reason=eligibility_reason,

            # Market confirmation (permission)
            market_confirmation_status=market_status,
            market_confirmation_reason=market_reason,

            # Decision engine output
            decision=asset["decision"],

            # Narrative snapshot
            narrative_summary=asset["narrative"],
        )

        candidates.append(candidate)

    return candidates