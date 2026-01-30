# marketmind/quant.py
# Robust price/indicator fetch with provider fallbacks (Finnhub → AlphaVantage → TwelveData)
# and local TA calculations (EMA/SMA/RSI/MACD) from daily closes.

import os, math, time, requests
from collections import deque
from dotenv import load_dotenv

load_dotenv()

FINNHUB_KEY   = os.getenv("FINNHUB_API_KEY", "")
AV_KEY        = os.getenv("ALPHAVANTAGE_API_KEY", "")
TWELVE_KEY    = os.getenv("TWELVEDATA_API_KEY", "")

FINNHUB_BASE  = "https://finnhub.io/api/v1"
AV_BASE       = "https://www.alphavantage.co/query"
TD_BASE       = "https://api.twelvedata.com"

# ---------- small helpers ----------

def _get_json(url, params, timeout=20):
    try:
        r = requests.get(url, params=params, timeout=timeout)
        r.raise_for_status()
        return r.json()
    except Exception:
        return None

# ---------- price (with fallbacks) ----------

def get_live_price(ticker: str) -> float:
    # 1) Finnhub quote
    if FINNHUB_KEY:
        j = _get_json(f"{FINNHUB_BASE}/quote", {"symbol": ticker, "token": FINNHUB_KEY})
        if j and isinstance(j, dict) and j.get("c"):
            try:
                return float(j["c"])
            except Exception:
                pass

    # 2) Alpha Vantage GLOBAL_QUOTE
    if AV_KEY:
        j = _get_json(AV_BASE, {"function":"GLOBAL_QUOTE","symbol":ticker,"apikey":AV_KEY})
        if j and "Global Quote" in j:
            try:
                return float(j["Global Quote"].get("05. price", 0.0) or 0.0)
            except Exception:
                pass

    # 3) Twelve Data price
    if TWELVE_KEY:
        j = _get_json(f"{TD_BASE}/price", {"symbol": ticker, "apikey": TWELVE_KEY})
        if j and "price" in j:
            try:
                return float(j["price"])
            except Exception:
                pass

    return 0.0

# ---------- candles (AV → TD; Finnhub omitted due to plan) ----------

def get_daily_closes(ticker: str, days: int = 400):
    """Return list of daily close prices (oldest→newest)."""
    # 1) Alpha Vantage TIME_SERIES_DAILY_ADJUSTED
    if AV_KEY:
        j = _get_json(AV_BASE, {
            "function":"TIME_SERIES_DAILY_ADJUSTED",
            "symbol": ticker,
            "outputsize": "full",
            "apikey": AV_KEY
        }, timeout=25)
        ts = j.get("Time Series (Daily)") if isinstance(j, dict) else None
        if ts:
            # AV gives newest→oldest dict keys; sort to oldest→newest
            dates = sorted(ts.keys())
            closes = []
            for d in dates[-days:]:
                try:
                    closes.append(float(ts[d]["4. close"]))
                except Exception:
                    pass
            if closes:
                return closes

    # 2) Twelve Data time_series
    if TWELVE_KEY:
        # request ~days+20 to ensure enough for indicators
        j = _get_json(f"{TD_BASE}/time_series",
                      {"symbol": ticker, "interval":"1day", "outputsize": str(days+30),
                       "order":"asc", "apikey": TWELVE_KEY}, timeout=25)
        data = j.get("values") if isinstance(j, dict) else None
        if data:
            closes = []
            for row in data:
                try:
                    closes.append(float(row["close"]))
                except Exception:
                    pass
            if closes:
                return closes[-days:]

    # fallback none
    return []

# ---------- local TA (provider-agnostic) ----------

def _sma(vals, n):
    if len(vals) < n or n <= 0:
        return None
    return sum(vals[-n:]) / float(n)

def _ema(vals, n):
    if len(vals) < n or n <= 0:
        return None
    k = 2.0 / (n + 1.0)
    # seed with SMA of first n
    ema = sum(vals[:n]) / n
    for x in vals[n:]:
        ema = x * k + ema * (1 - k)
    return ema

def _rsi(vals, n=14):
    if len(vals) < n + 1:
        return None
    gains, losses = 0.0, 0.0
    # seed
    for i in range(1, n+1):
        ch = vals[i] - vals[i-1]
        if ch >= 0:
            gains += ch
        else:
            losses -= ch
    avg_gain = gains / n
    avg_loss = losses / n
    # Wilder’s smoothing
    for i in range(n+1, len(vals)):
        ch = vals[i] - vals[i-1]
        gain = max(ch, 0.0)
        loss = max(-ch, 0.0)
        avg_gain = (avg_gain*(n-1) + gain) / n
        avg_loss = (avg_loss*(n-1) + loss) / n
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return 100.0 - (100.0 / (1.0 + rs))

def _macd_hist(vals, fast=12, slow=26, signal=9):
    if len(vals) < slow + signal:
        return None
    ema_fast = _ema(vals, fast)
    ema_slow = _ema(vals, slow)
    if ema_fast is None or ema_slow is None:
        return None
    macd_line = ema_fast - ema_slow
    # To compute signal line properly we’d need full MACD series.
    # Approximate by recomputing with partial history:
    macd_series = []
    for i in range(slow, len(vals)+1):
        ef = _ema(vals[:i], fast)
        es = _ema(vals[:i], slow)
        macd_series.append(ef - es)
    signal_line = _ema(macd_series, signal)
    if signal_line is None:
        return None
    return macd_line - signal_line

# ---------- public API ----------

def fetch_technical_indicators(ticker: str) -> dict:
    closes = get_daily_closes(ticker, days=400)
    price  = get_live_price(ticker)

    ema20  = _ema(closes, 20)   or 0.0
    sma50  = _sma(closes, 50)   or 0.0
    sma200 = _sma(closes, 200)  or 0.0
    rsi14  = _rsi(closes, 14)   or 0.0
    macdh  = _macd_hist(closes, 12, 26, 9) or 0.0

    return {
        "Price": round(float(price), 4),
        "EMA20": round(float(ema20), 4),
        "SMA50": round(float(sma50), 4),
        "SMA200": round(float(sma200), 4),
        "RSI": round(float(rsi14), 4),
        "MACD_Hist": round(float(macdh), 4),
    }
