# test_phase5c.py

from marketmind_engine.analysis.domain.intention_domain import IntentionDomain
from marketmind_engine.analysis.domain.asset_ripple import AssetRipple
from marketmind_engine.analysis.domain.marketstate_projector import (
    project_ripples_to_marketstate
)
from marketmind_engine.decision.decision_engine import DecisionEngine
from marketmind_engine.decision.confirmation import confirm_market_capacity
from marketmind_engine.decision.state import MarketState

print("=== Phase-5C Integration Test ===")

# -------------------------------
# Synthetic domain
# -------------------------------
domain = IntentionDomain(
    name="Defense AI",
    fils=0.65,
    ucip=0.75,
    ttcf=0.20,
)

# -------------------------------
# Static ripples
# -------------------------------
ripples = [
    AssetRipple(symbol="PLTR", domain="Defense AI", strength=0.85, reason="static"),
    AssetRipple(symbol="LMT",  domain="Defense AI", strength=0.75, reason="static"),
    AssetRipple(symbol="RTX",  domain="Defense AI", strength=0.70, reason="static"),
]

# -------------------------------
# Project to MarketState (Phase-4F / 5A)
# -------------------------------
states = project_ripples_to_marketstate(domain, ripples)

print("\nProjected MarketStates:")
for s in states:
    print(s.symbol, round(s.fils, 3), round(s.ucip, 3), round(s.ttcf, 3))

# -------------------------------
# Inject market capacity (Phase-5C)
# NOTE: MarketState is immutable → rebuild states
# -------------------------------
states_with_capacity = []

for s in states:
    states_with_capacity.append(
        MarketState(
            symbol=s.symbol,
            domain=domain.name,            # 🔑 REQUIRED FOR PHASE-6+
            narrative=s.narrative,

            fils=s.fils,
            ucip=s.ucip,
            ttcf=s.ttcf,

            fractal_levels=s.fractal_levels,

            data_source=s.data_source,
            engine_id=s.engine_id,
            timestamp_utc=s.timestamp_utc,

            # Phase-5C: quant as permission only
            liquidity=0.80,
            volatility=0.30,
            responsiveness=0.60,
        )
    )

states = states_with_capacity

# -------------------------------
# Confirmation test
# -------------------------------
print("\nMarket confirmation:")
for s in states:
    c = confirm_market_capacity(s)
    print(s.symbol, c.confirmed, c.reason)

# -------------------------------
# Decision engine test
# -------------------------------
engine = DecisionEngine()

print("\nDecision engine results:")
for s in states:
    result = engine.evaluate(s)
    print(
        s.symbol,
        result.decision,
        result.metadata["eligible"],
        result.metadata["market_confirmed"],
    )

print("\n=== TEST COMPLETE ===")