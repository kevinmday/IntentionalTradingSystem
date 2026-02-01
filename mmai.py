import os
import sys
import subprocess

# ------------------------------------------------------------------
# Ensure project root is on PYTHONPATH
# ------------------------------------------------------------------
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# ------------------------------------------------------------------
# Engine authority (execution now flows through engine)
# ------------------------------------------------------------------
from marketmind_engine.main import run_module

# ------------------------------------------------------------------
# Flask-specific wiring
# IMPORTANT:
# This file serves TWO roles:
#   1) Flask bootstrap (imported by Flask)
#   2) CLI launcher (python mmai.py <module>)
#
# Flask wiring MUST NOT run in CLI mode.
# ------------------------------------------------------------------
if __name__ != "__main__":
    from routes import dual_card_bp  # import the blueprint
    app.register_blueprint(dual_card_bp)

# ------------------------------------------------------------------
# Legacy module registry (UNCHANGED)
# ------------------------------------------------------------------
MODULES = {
    # ✅ Trader + Metrics BOTH start the main Flask service
    "trader":  r"MarketMindAI\MarketMindTrader\marketmind_trader_main.py",
    "metrics": r"MarketMindAI\MarketMindTrader\marketmind_trader_main.py",

    # ✅ Seeder scripts
    "seeder1": r"MarketMindAI\MarketMindData\market_mind_data\marketmind_data_seeder.py",
    "seeder2": r"MarketMindAI\MarketMindData\market_mind_data\marketmind_seeder_app_ver15.py",
    "seeder3": r"MarketMindAI\MarketMindData\marketmind_data_seeder.py",
    "seeder4": r"MarketMindAI\MarketMindData\market_mind_data_seeder.py",

    # ✅ Utility scripts
    "rss":     r"MarketMindAI\MarketMindTrader\marketmind\rss_parser.py",
    "agents":  r"MarketMindAI\marketmind_agents\main.py",
    "tagger":  r"MarketMindAI\intention_tagger.py",
    "stream":  r"MarketMindAI\StreamMonitor.py",
}

# ------------------------------------------------------------------
# Legacy behavior (PRESERVED VERBATIM)
# ------------------------------------------------------------------
def _legacy_run_module(name):
    if name not in MODULES:
        print(f"[!] Unknown module '{name}'. Options: {', '.join(MODULES.keys())}")
        sys.exit(1)

    target = MODULES[name]
    print(f"[INFO] Launching module: {name} -> {target}")
    subprocess.run([sys.executable, target])

# ------------------------------------------------------------------
# Bind legacy behavior to engine passthrough
# (engine calls this internally for now)
# ------------------------------------------------------------------
run_module.__wrapped__ = _legacy_run_module

# ------------------------------------------------------------------
# CLI entrypoint (UNCHANGED BEHAVIOR)
# ------------------------------------------------------------------
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(
            f"Usage: python mmai.py <module>\n"
            f"Available: {', '.join(MODULES.keys())}"
        )
        sys.exit(1)

    # ✅ Execution now flows through the engine
    run_module(sys.argv[1])
