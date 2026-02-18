"""
Engine Entrypoint (Authoritative Runtime)

This file owns:

- Engine session state
- Deterministic engine tick
- Explicit module dispatch (repo-local ONLY)
- Environment boundary (broker credentials)

STRICT RULE:
This launcher may ONLY execute modules inside the current
IntentionalTradingSystem repository tree.

No legacy MarketMindAI tree.
No OneDrive paths.
No external dispatch.
"""

import sys
import subprocess
import os
from pathlib import Path

# -------------------------------------------------------------------
# Resolve Repository Root (authoritative)
# -------------------------------------------------------------------

ENGINE_DIR = Path(__file__).resolve().parent
REPO_ROOT = ENGINE_DIR.parent  # C:\dev\IntentionalTradingSystem

# -------------------------------------------------------------------
# Environment Boundary (ONLY place env is loaded)
# -------------------------------------------------------------------

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
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
    This is the authoritative causal clock.
    """
    global _engine_tick
    _engine_tick += 1
    return _engine_tick


# -------------------------------------------------------------------
# Module Dispatch Table (REPO-LOCAL ONLY)
# -------------------------------------------------------------------
#
# All paths are relative to REPO_ROOT.
# These MUST exist inside C:\dev\IntentionalTradingSystem
#
# Add modules here intentionally.
# Do NOT reference MarketMindAI legacy tree.
# -------------------------------------------------------------------

MODULES = {

    # Runtime UI (Phase 11+)
    "runtime": REPO_ROOT / "runtime" / "app.py",

    # Future: add new modules explicitly here
    # Example:
    # "agents": REPO_ROOT / "marketmind_engine" / "agents" / "main.py",
}


# -------------------------------------------------------------------
# Broker Validation (only if explicitly required)
# -------------------------------------------------------------------

def validate_broker_requirements(module_name: str):
    """
    Validate broker credentials only when required.
    Currently no module requires it.
    """
    # Placeholder for future broker-gated modules
    return


# -------------------------------------------------------------------
# Launch Guard
# -------------------------------------------------------------------

def _validate_repo_local(path: Path):
    """
    Ensure the target file lives inside this repository.
    Prevents shadow/legacy execution.
    """
    try:
        path.resolve().relative_to(REPO_ROOT.resolve())
    except Exception:
        print("[ENGINE] Refusing to launch non-repo-local module:")
        print(f"         {path}")
        sys.exit(1)


# -------------------------------------------------------------------
# Launcher
# -------------------------------------------------------------------

def run_module(name: str):
    """
    Launch a registered module in a subprocess.

    This keeps:
    - Engine isolated
    - Flask isolated
    - Import side-effects contained
    """

    if name not in MODULES:
        print(f"[ENGINE] Unknown module '{name}'.")
        print(f"[ENGINE] Available modules: {', '.join(MODULES.keys())}")
        sys.exit(1)

    target_path = Path(MODULES[name])

    if not target_path.exists():
        print(f"[ENGINE] Target file not found: {target_path}")
        sys.exit(1)

    _validate_repo_local(target_path)

    validate_broker_requirements(name)

    print(f"[ENGINE] Launching module: {name}")
    print(f"[ENGINE] Path: {target_path}")

    subprocess.run(
        [sys.executable, str(target_path)],
        cwd=str(REPO_ROOT),
        check=False,
    )


# -------------------------------------------------------------------
# CLI Entrypoint
# -------------------------------------------------------------------

if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("[ENGINE] No module specified.")
        print("[ENGINE] Usage:")
        print("    python -m marketmind_engine <module>")
        print()
        print(f"[ENGINE] Available modules: {', '.join(MODULES.keys())}")
        sys.exit(1)

    run_module(sys.argv[1])