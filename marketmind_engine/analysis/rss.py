# marketmind/rss_parser.py
"""
Lightweight RSS utilities for MarketMind.

- parse_default_rss() -> List[Dict]: fetches & parses a curated set of feeds.
- fetch_article_text(url: str) -> str: best-effort full-text scrape for an article.

Both functions are defensive and log with the "[RSS]" prefix used elsewhere.
"""

from __future__ import annotations

import re
from typing import Dict, List, Optional

import feedparser
import requests
from bs4 import BeautifulSoup

# ------------------------ Config ------------------------

# Rotate / expand as you like. These are generic, low-friction sources.
RSS_FEEDS: List[str] = [
    "https://rss.cnn.com/rss/edition.rss",
    "https://feeds.reuters.com/reuters/topNews",
    # Add or modify your feed URLs here
]

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0 Safari/537.36"
)
TIMEOUT = 12  # seconds

# ------------------------ Helpers ------------------------


def _http_get(url: str) -> Optional[requests.Response]:
    """GET with sane headers/timeouts and quiet failure."""
    try:
        resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=TIMEOUT)
        resp.raise_for_status()
        return resp
    except Exception as e:
        print(f"[RSS] HTTP error for {url}: {e}")
        return None


def _normalize_entry(entry) -> Dict:
    """Normalize a feedparser entry to a compact dict."""
    # feedparser returns a dict-like object
    title = entry.get("title", "").strip()
    link = entry.get("link", "").strip()
    published = entry.get("published", entry.get("updated", "")) or "No date"
    summary = entry.get("summary", "") or ""
    # Remove any HTML tags in summary for a quick, readable blurb.
    summary = re.sub(r"<[^>]+>", "", summary).strip()
    return {
        "title": title,
        "link": link,
        "published": published,
        "summary": summary,
    }


def _strip_visible_text(html: bytes | str) -> str:
    """Extract readable text from raw HTML bytes/str."""
    soup = BeautifulSoup(html, "lxml")

    # Remove obvious noise
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    # Prefer article content if present
    article = soup.find("article")
    container = article if article else soup

    parts = [p.get_text(" ", strip=True) for p in container.find_all("p")]
    text = "\n".join(p for p in parts if p)
    text = re.sub(r"\n{2,}", "\n\n", text).strip()
    return text


# ------------------------ Public API ------------------------


def parse_default_rss() -> List[Dict]:
    """
    Fetch and parse all RSS_FEEDS.

    Returns
    -------
    List[Dict]
        Each dict has: { title, link, published, summary }
    """
    all_entries: List[Dict] = []

    for url in RSS_FEEDS:
        print(f"[RSS] Fetching: {url}")
        resp = _http_get(url)
        if not resp:
            print(f"[RSS] 0 entries from {url}")
            continue

        feed = feedparser.parse(resp.content)

        if getattr(feed, "bozo", False):
            # bozo_exception may be noisy; print short form if available
            err = getattr(feed, "bozo_exception", None)
            print(f"[RSS] Warning: parse anomaly for {url}: {err}")

        entries = [ _normalize_entry(e) for e in feed.entries or [] ]
        all_entries.extend(entries)
        print(f"[RSS] {len(entries)} entries from {url}")

    return all_entries


def fetch_article_text(url: str) -> str:
    """
    Attempt to fetch & extract readable text for a single article URL.

    Returns a best-effort plain-text body (may be empty on heavily scripted/paywalled sites).
    """
    try:
        resp = _http_get(url)
        if not resp:
            return ""
        text = _strip_visible_text(resp.content)
        return text
    except Exception as e:
        print(f"[RSS] Article extract failed for {url}: {e}")
        return ""


# ------------------------ Manual test ------------------------

if __name__ == "__main__":
    # Quick manual run: fetch feeds and preview first items
    items = parse_default_rss()
    print(f"\n[RSS] Total combined entries: {len(items)}")
    for i, item in enumerate(items[:5], 1):
        print(f"{i}. {item['title']}  ({item['published']})")
        print(f"   {item['link']}")
        print(f"   {item['summary'][:140]}{'…' if len(item['summary'])>140 else ''}\n")

    # Optional: try article extraction on the first link
    if items:
        sample_url = items[0]["link"]
        print(f"[RSS] Extract preview from: {sample_url}")
        body = fetch_article_text(sample_url)
        print(body[:1500])
