from marketmind_engine.candidates.types import Candidate
from marketmind_engine.decision.confirmation import confirm_market_capacity
from marketmind_engine.decision.eligibility import evaluate_eligibility
from marketmind_engine.decision.decision_engine import DecisionEngine
from marketmind_engine.decision.state import MarketState
from marketmind_engine.core.clock import ENGINE_CLOCK


def materialize_candidate(
    state: MarketState,
    engine: DecisionEngine,
) -> Candidate:
    """
    Assemble a Candidate from a fully-evaluated MarketState.
    """

    eligibility = evaluate_eligibility(state)
    confirmation = confirm_market_capacity(state)
    decision = engine.evaluate(state)

    return Candidate(
        symbol=state.symbol,
        domain=state.domain,

        fils=state.fils,
        ucip=state.ucip,
        ttcf=state.ttcf,

        eligible=eligibility.eligible,
        eligibility_reason=eligibility.reason,

        market_confirmed=confirmation.confirmed,
        market_confirmation_reason=confirmation.reason,

        decision=decision.decision,

        engine_time=ENGINE_CLOCK.now()["engine_time"],
    )