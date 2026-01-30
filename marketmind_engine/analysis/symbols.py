import os
import json
import threading
import time
import requests

# Polygon.io API Key
POLYGON_API_KEY = os.getenv("POLYGON_API_KEY", "13U6bDmdI_kUH7T7_iPeo6ydsT4Qg2Lx")

# Local cache file
TICKER_CACHE_FILE = os.path.join(os.path.dirname(__file__), "ticker_cache.json")

# Global in-memory set
VALID_TICKERS = set()

# ------------------------------
# FETCH FROM POLYGON.IO
# ------------------------------
def fetch_polygon_tickers():
    """
    Fetch all actively traded US tickers from Polygon.io
    Auto-paginates until all tickers are retrieved.
    """
    url = f"https://api.polygon.io/v3/reference/tickers?market=stocks&active=true&limit=1000&apiKey={POLYGON_API_KEY}"
    tickers = []
    while url:
        resp = requests.get(url, timeout=10)
        if resp.status_code != 200:
            print(f"[TICKER CACHE] Polygon API error: {resp.text}")
            break

        data = resp.json()
        tickers.extend([t["ticker"] for t in data.get("results", []) if t.get("ticker")])

        url = data.get("next_url")
        if url:  # append API key for next page
            url += f"&apiKey={POLYGON_API_KEY}"

    print(f"[TICKER CACHE] ✅ Polygon fetched {len(tickers)} tickers")
    return tickers

# ------------------------------
# STATIC INDEX LISTS (Fallback)
# ------------------------------
def fetch_sp500_list():
    return [
        "AAPL", "MSFT", "AMZN", "NVDA", "GOOGL", "META", "TSLA", "BRK.B", "UNH", "JNJ",
        "V", "XOM", "JPM", "PG", "MA", "LLY", "HD", "MRK", "PEP", "ABBV",
        # … extend to full 500 later
    ]

def fetch_nasdaq100_list():
    return [
        "AAPL", "MSFT", "NVDA", "AMZN", "META", "GOOG", "GOOGL", "TSLA", "AVGO", "ADBE",
        "NFLX", "INTC", "AMD", "CSCO", "PDD", "QCOM", "SBUX", "AMAT", "PYPL", "BKNG",
        # … extend rest of NASDAQ-100
    ]

def fetch_nyse100_list():
    return [
        "BA", "CAT", "KO", "MCD", "GE", "IBM", "UPS", "MMM", "CVX", "WMT",
        "GS", "MS", "AXP", "DIS", "RTX", "DOW", "NKE", "HON", "FDX", "T",
        # … extend rest of NYSE-100
    ]

def merge_static_lists():
    """Combine S&P500, NASDAQ100, and NYSE100 for fallback"""
    return list(set(fetch_sp500_list() + fetch_nasdaq100_list() + fetch_nyse100_list()))

# ------------------------------
# HYBRID FETCH LOGIC
# ------------------------------
def fetch_latest_tickers():
    """
    Hybrid fetch:
    1. Try Polygon.io live tickers
    2. If Polygon fails, merge static lists
    3. If all else fails, return minimal 10
    """
    # Try Polygon first
    try:
        polygon_tickers = fetch_polygon_tickers()
        if polygon_tickers:
            return polygon_tickers
        raise RuntimeError("Polygon returned 0 tickers")
    except Exception as e:
        print(f"[TICKER CACHE] Polygon fetch failed → fallback. {e}")

    # Try static merged lists
    try:
        merged = merge_static_lists()
        if merged:
            print(f"[TICKER CACHE] ✅ Static merge → {len(merged)} tickers")
            return merged
    except Exception as e:
        print(f"[TICKER CACHE] Static fallback failed → {e}")

    # Last-resort fallback
    return [
        "AAPL", "MSFT", "NVDA", "TSLA", "META",
        "GOOGL", "AMZN", "PLTR", "QCOM", "INTC"
    ]

# ------------------------------
# LOAD & SAVE CACHE
# ------------------------------
def load_cached_tickers():
    global VALID_TICKERS
    if os.path.exists(TICKER_CACHE_FILE):
        try:
            with open(TICKER_CACHE_FILE, "r") as f:
                data = json.load(f)
            VALID_TICKERS = set(data.get("tickers", []))
            print(f"[TICKER CACHE] Loaded {len(VALID_TICKERS)} tickers from cache")
        except Exception as e:
            print(f"[TICKER CACHE] Failed to load cache: {e}")
    else:
        print("[TICKER CACHE] No cache file found, starting empty.")

def save_cached_tickers():
    try:
        with open(TICKER_CACHE_FILE, "w") as f:
            json.dump({"tickers": list(VALID_TICKERS)}, f, indent=2)
        print(f"[TICKER CACHE] Saved {len(VALID_TICKERS)} tickers to cache")
    except Exception as e:
        print(f"[TICKER CACHE] Failed to save cache: {e}")

# ------------------------------
# REFRESH LOGIC
# ------------------------------
def refresh_valid_tickers():
    """Refresh global VALID_TICKERS with hybrid fetch and persist to disk."""
    global VALID_TICKERS
    fresh_set = set(fetch_latest_tickers())
    if fresh_set:
        VALID_TICKERS = fresh_set
        save_cached_tickers()
        print(f"[TICKER CACHE] ✅ Refreshed VALID_TICKERS → {len(VALID_TICKERS)} tickers")

# ------------------------------
# BACKGROUND REFRESH LOOP
# ------------------------------
def start_background_refresh(interval_hours=6):
    """Refresh tickers periodically (default every 6h)."""
    def refresh_loop():
        while True:
            time.sleep(interval_hours * 3600)
            print("[TICKER CACHE] Periodic refresh starting...")
            refresh_valid_tickers()
    threading.Thread(target=refresh_loop, daemon=True).start()

# ------------------------------
# PUBLIC MANUAL REFRESH ROUTE
# ------------------------------
def manual_refresh_tickers():
    """Manually triggers a refresh and returns updated count."""
    global VALID_TICKERS
    print("[TICKER REFRESH] Manual refresh requested…")

    tickers = fetch_latest_tickers()
    VALID_TICKERS = set(tickers)
    save_cached_tickers()

    return {"status": "success", "ticker_count": len(VALID_TICKERS)}

# ------------------------------
# INIT ON IMPORT
# ------------------------------
def init_ticker_cache():
    """Initialize ticker cache at app startup."""
    load_cached_tickers()
    if not VALID_TICKERS:
        refresh_valid_tickers()
    start_background_refresh()
