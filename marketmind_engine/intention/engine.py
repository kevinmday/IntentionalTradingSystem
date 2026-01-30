# marketmind/intention_engine.py

import os, sys

# ✅ Dynamically locate the MarketMindAI project root
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))       # /marketmind
TRADER_DIR = os.path.dirname(CURRENT_DIR)                      # /MarketMindTrader
ROOT_DIR = os.path.dirname(TRADER_DIR)                         # /MarketMindAI
METRICS_PATH = os.path.join(ROOT_DIR, "marketmind_metrics")

# ✅ Ensure metrics folder is in sys.path once
if METRICS_PATH not in sys.path:
    sys.path.insert(0, METRICS_PATH)

# ✅ Import from metrics safely (no circular loops)
from equation_engine import (
    compute_ucip,
    bell_drake_threshold,
    fractal_cascade,
    compute_fils_from_narrative  # will call fils_engine internally
)


def generate_trade_metrics(narrative: str, ripple_domain: str) -> dict:
    """
    Generate intention metrics for a given RSS narrative:
      - FILS (Future Intention Likelihood Scale)
      - UCIP (Fractal resonance strength)
      - TTCF (Chaos noise factor)
      - Drift (fractal cascade)
      - BellDrake threshold trigger
      - Signal (BUY / SELL / Watch)
    """

    # ✅ Step 1: NLP analysis for FILS, UCIP, TTCF
    fils_data = compute_fils_from_narrative(narrative)

    fils_score = fils_data["FILS"]
    ucip_value = fils_data["UCIP"]
    ttcf_score = fils_data["TTCF"]

    # ✅ Step 2: Drift via fractal cascade
    drift_levels = fractal_cascade(fils_score, depth=3)
    drift_score = drift_levels[0] if drift_levels else 0.0

    # ✅ Step 3: Bell-Drake threshold – did it reach macro impact?
    threshold_hit = bell_drake_threshold(drift_levels, threshold=1.2)

    # ✅ Step 4: Simple signal classification
    if fils_score > 0.65 and ucip_value > 0.55:
        signal = "BUY"
    elif fils_score < 0.35 and ttcf_score > 0.6:
        signal = "SELL"
    else:
        signal = "Watch"

    return {
        "FILS": round(fils_score, 4),
        "UCIP": round(ucip_value, 4),
        "TTCF": round(ttcf_score, 4),
        "Drift": round(drift_score, 4),
        "BellDrake": threshold_hit,
        "Signal": signal
    }
