# marketmind/rss_cache.py

"""
Lightweight in-memory cache for RSS entries.

All fetching/parsing is centralized in `rss_parser.parse_default_rss`.
This module only handles caching + simple refresh semantics so that
routes/endpoints can call `refresh_rss_cache()` without duplicating logic.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Optional

# Single source of truth for feeds & parsing:
from marketmind_engine.analysis.rss import parse_default_rss

# --- Cache state -------------------------------------------------------------

latest_rss_entries: List[Dict[str, Any]] = []
_last_refresh: Optional[datetime] = None

# Minimum time between auto refreshes (if you add a "get" that refreshes lazily)
_REFRESH_MIN_INTERVAL = timedelta(seconds=90)


# --- Public API --------------------------------------------------------------

def refresh_rss_cache(force: bool = True) -> List[Dict[str, Any]]:
    """
    Fetch latest RSS entries using the unified parser and store them in-memory.

    Parameters
    ----------
    force : bool
        If False, will skip refresh when the last refresh is recent
        (see _REFRESH_MIN_INTERVAL). Default True (always refresh).

    Returns
    -------
    List[Dict[str, Any]]
        The list of normalized RSS entries (title, summary, link, published?).
    """
    global latest_rss_entries, _last_refresh

    now = datetime.now(timezone.utc)
    if not force and _last_refresh and (now - _last_refresh) < _REFRESH_MIN_INTERVAL:
        return latest_rss_entries

    try:
        entries = parse_default_rss()
        # Ensure it's a list of dicts even if parser had an empty result
        if isinstance(entries, list):
            latest_rss_entries = entries
        else:
            latest_rss_entries = []
        _last_refresh = now
    except Exception as exc:
        # Keep old cache on failure; just log to console
        print(f"[RSS] refresh_rss_cache() failed: {exc}")

    return latest_rss_entries


def get_rss_cache() -> List[Dict[str, Any]]:
    """
    Return the most recently cached RSS entries without triggering a refresh.
    Use `refresh_rss_cache()` when you want to update the cache.
    """
    return latest_rss_entries


def last_refresh_iso() -> Optional[str]:
    """
    ISO8601 string for last refresh time (UTC), or None if never refreshed.
    """
    return _last_refresh.isoformat() if _last_refresh else None


__all__ = [
    "refresh_rss_cache",
    "get_rss_cache",
    "last_refresh_iso",
    "latest_rss_entries",
]
