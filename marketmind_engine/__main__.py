"""
Package execution entrypoint.

Allows:
    python -m marketmind_engine <module>
"""

from .main import run_module
import sys

if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("[ENGINE] No module specified.")
        print("Usage:")
        print("    python -m marketmind_engine <module>")
        sys.exit(1)

    run_module(sys.argv[1])