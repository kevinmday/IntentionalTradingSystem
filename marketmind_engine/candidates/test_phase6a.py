from marketmind_engine.candidates.materializer import materialize_candidates
from test_phase5c import states

print("=== Phase-6A Candidate Materialization Test ===")

candidates = materialize_candidates(states)

for c in candidates:
    print(
        f"{c.symbol:<5}",
        f"domain={c.domain:<12}",
        f"decision={c.decision:<9}",
        f"eligible={c.eligible}",
        f"market_ok={c.market_confirmed}",
    )

print("=== TEST COMPLETE ===")