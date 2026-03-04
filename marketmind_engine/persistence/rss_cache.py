"""
RSS Cache (Engine Layer)

Lightweight in-memory cache for RSS entries.

All fetching/parsing is centralized in:
    marketmind_engine.analysis.rss.parse_default_rss

This module handles:
- Cache storage
- Controlled refresh semantics
- Timestamp tracking

No Flask logic.
No runtime logic.
Engine-layer only.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Optional

# Single source of truth for feeds & parsing
from marketmind_engine.analysis.rss import parse_default_rss


# -----------------------------------------------------------------------------
# Cache State
# -----------------------------------------------------------------------------

_latest_rss_entries: List[Dict[str, Any]] = []
_last_refresh: Optional[datetime] = None

# Minimum interval between auto refreshes (if force=False)
_REFRESH_MIN_INTERVAL = timedelta(seconds=90)


# -----------------------------------------------------------------------------
# Public API
# -----------------------------------------------------------------------------

def refresh_rss_cache(force: bool = True) -> List[Dict[str, Any]]:
    """
    Fetch latest RSS entries using the unified parser
    and store them in memory.

    Parameters
    ----------
    force : bool
        If False, skip refresh when last refresh is recent.

    Returns
    -------
    List[Dict[str, Any]]
        Normalized RSS entries.
    """
    global _latest_rss_entries, _last_refresh

    now = datetime.now(timezone.utc)

    if (
        not force
        and _last_refresh
        and (now - _last_refresh) < _REFRESH_MIN_INTERVAL
    ):
        return _latest_rss_entries

    try:
        entries = parse_default_rss()

        if isinstance(entries, list):
            _latest_rss_entries = entries
        else:
            _latest_rss_entries = []

        _last_refresh = now

    except Exception as exc:
        # Keep previous cache if fetch fails
        print(f"[RSS] refresh_rss_cache() failed: {exc}")

    return _latest_rss_entries


def get_rss_cache() -> List[Dict[str, Any]]:
    """
    Return cached RSS entries without triggering refresh.
    """
    return _latest_rss_entries


def last_refresh_iso() -> Optional[str]:
    """
    ISO8601 UTC timestamp of last refresh.
    """
    return _last_refresh.isoformat() if _last_refresh else None


__all__ = [
    "refresh_rss_cache",
    "get_rss_cache",
    "last_refresh_iso",
]
