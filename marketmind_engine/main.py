"""
Engine entrypoint (launcher authority).

This file owns:
- Engine session state
- Deterministic engine tick
- Explicit module dispatch
- Environment boundary (broker credentials)

Legacy mmai.py is intentionally NOT imported.
All launched modules must be import-safe.
"""

import sys
import subprocess
import os
from pathlib import Path

# -------------------------------------------------------------------
# Environment Boundary (ONLY place env is loaded)
# -------------------------------------------------------------------

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    # dotenv optional — system env still supported
    pass

TRADIER_TOKEN = os.getenv("TRADIER_TOKEN")
TRADIER_SANDBOX = os.getenv("TRADIER_SANDBOX", "true").lower() == "true"

# -------------------------------------------------------------------
# Engine-owned monotonic tick (session-scoped, deterministic)
# -------------------------------------------------------------------

_engine_tick = 0

def next_tick() -> int:
    """
    Advance and return the engine monotonic tick.
    This is the authoritative causal clock for MMAI.
    """
    global _engine_tick
    _engine_tick += 1
    return _engine_tick


# -------------------------------------------------------------------
# Module dispatch table (explicit, auditable)
# -------------------------------------------------------------------

MODULES = {
    # Trader + Metrics BOTH start the main Flask service
    "trader":  r"MarketMindAI\MarketMindTrader\marketmind_trader_main.py",
    "metrics": r"MarketMindAI\MarketMindTrader\marketmind_trader_main.py",

    # Seeder scripts
    "seeder1": r"MarketMindAI\MarketMindData\market_mind_data\marketmind_data_seeder.py",
    "seeder2": r"MarketMindAI\MarketMindData\market_mind_data\marketmind_seeder_app_ver15.py",
    "seeder3": r"MarketMindAI\MarketMindData\marketmind_data_seeder.py",
    "seeder4": r"MarketMindAI\MarketMindData\market_mind_data_seeder.py",

    # Utility / support scripts
    "rss":     r"MarketMindAI\MarketMindTrader\marketmind\rss_parser.py",
    "agents":  r"MarketMindAI\marketmind_agents\main.py",
    "tagger":  r"MarketMindAI\intention_tagger.py",
    "stream":  r"MarketMindAI\StreamMonitor.py",
}


# -------------------------------------------------------------------
# Broker Validation (only if trader module invoked)
# -------------------------------------------------------------------

def validate_broker_requirements(module_name: str):
    """
    Validate broker credentials ONLY when required.
    Does not affect deterministic engine logic.
    """
    if module_name in ("trader", "metrics"):
        if not TRADIER_TOKEN:
            print("[ENGINE] TRADIER_TOKEN not found in environment.")
            print("[ENGINE] Set it via:")
            print("    setx TRADIER_TOKEN \"your_token_here\"")
            sys.exit(1)

        print("[ENGINE] Tradier token detected.")
        print(f"[ENGINE] Sandbox mode: {TRADIER_SANDBOX}")


# -------------------------------------------------------------------
# Launcher
# -------------------------------------------------------------------

def run_module(name: str):
    """
    Launch a registered MMAI module in a subprocess.

    This keeps:
    - Engine isolated
    - Flask isolated
    - Import side-effects contained
    """

    if name not in MODULES:
        print(f"[ENGINE] Unknown module '{name}'.")
        print(f"[ENGINE] Available modules: {', '.join(MODULES.keys())}")
        sys.exit(1)

    validate_broker_requirements(name)

    target = MODULES[name]
    resolved_path = Path(target)

    if not resolved_path.exists():
        print(f"[ENGINE] Target file not found: {resolved_path}")
        sys.exit(1)

    print(f"[ENGINE] Launching module: {name} -> {target}")

    subprocess.run([sys.executable, str(resolved_path)], check=False)


# -------------------------------------------------------------------
# CLI entrypoint
# -------------------------------------------------------------------

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("[ENGINE] No module specified.")
        print(f"[ENGINE] Usage: python -m marketmind_engine <module>")
        print(f"[ENGINE] Available modules: {', '.join(MODULES.keys())}")
        sys.exit(1)

    run_module(sys.argv[1])