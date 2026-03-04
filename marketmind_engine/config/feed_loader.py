"""
Feed Loader

Responsible for loading and validating feed configuration
from feeds.yaml.

This module does NOT parse feeds.
It only loads configuration.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Dict, Any
import yaml


# -----------------------------------------------------------------------------
# FeedConfig Dataclass
# -----------------------------------------------------------------------------

@dataclass(frozen=True)
class FeedConfig:
    id: str
    type: str
    domain: str
    weight: float
    enabled: bool
    url: Optional[str] = None
    source: Optional[str] = None


# -----------------------------------------------------------------------------
# Loader
# -----------------------------------------------------------------------------

DEFAULT_CONFIG_PATH = (
    Path(__file__).resolve().parent / "feeds.yaml"
)


def load_feed_config(path: Optional[Path] = None) -> List[FeedConfig]:
    """
    Load feeds.yaml and return a list of FeedConfig objects.

    Returns only enabled feeds.
    Fails safely (returns empty list on error).
    """

    config_path = path or DEFAULT_CONFIG_PATH

    if not config_path.exists():
        print(f"[FEEDS] Config file not found: {config_path}")
        return []

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            raw = yaml.safe_load(f) or {}

    except Exception as e:
        print(f"[FEEDS] Failed to load YAML: {e}")
        return []

    feeds_raw = raw.get("feeds", [])
    global_cfg = raw.get("global", {})

    default_weight = global_cfg.get("default_weight", 1.0)

    feed_configs: List[FeedConfig] = []

    for feed in feeds_raw:

        try:
            enabled = feed.get("enabled", True)
            if not enabled:
                continue

            feed_configs.append(
                FeedConfig(
                    id=feed["id"],
                    type=feed["type"],
                    domain=feed["domain"],
                    weight=feed.get("weight", default_weight),
                    enabled=enabled,
                    url=feed.get("url"),
                    source=feed.get("source"),
                )
            )

        except KeyError as missing:
            print(f"[FEEDS] Missing required field: {missing}")
            continue

    return feed_configs


# -----------------------------------------------------------------------------
# Utility
# -----------------------------------------------------------------------------

def load_feeds_by_type(feed_type: str) -> List[FeedConfig]:
    """
    Convenience filter.
    """
    return [f for f in load_feed_config() if f.type == feed_type]
