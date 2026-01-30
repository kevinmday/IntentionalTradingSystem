# marketmind/services/alpaca_client.py
"""
Alpaca integration (alpaca-py v2) for MarketMindTrader.

- Uses .env: ALPACA_API_KEY, ALPACA_API_SECRET, ALPACA_PAPER (1|0)
- Provides lazy-inited clients and small last-price cache
- Back-compat shims: _get_trading_client(), _alpaca_last_price()
"""

from __future__ import annotations
import os
import time
import logging
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv

# --- Alpaca v2 SDK ---
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockLatestTradeRequest
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest, GetOrdersRequest
from alpaca.trading.enums import OrderSide, TimeInForce, QueryOrderStatus

# Load environment once (safe if already loaded elsewhere)
load_dotenv()

# ---- Globals (lazy init) ----
_ALPACA_DATA_CLIENT: Optional[StockHistoricalDataClient] = None
_TRADING_CLIENT: Optional[TradingClient] = None

# Simple 10s last-price cache: { "NVDA": (timestamp, price_float) }
_PRICE_CACHE: Dict[str, tuple[float, float]] = {}

# ---- Internal: credentials ----
def _creds() -> tuple[str, str, bool]:
    k = os.getenv("ALPACA_API_KEY") or os.getenv("APCA_API_KEY_ID") or ""
    s = os.getenv("ALPACA_API_SECRET") or os.getenv("APCA_API_SECRET_KEY") or ""
    paper = (os.getenv("ALPACA_PAPER", "1") != "0")
    if not k or not s:
        logging.getLogger(__name__).warning("ALPACA creds missing (ALPACA_API_KEY / ALPACA_API_SECRET)")
    return k, s, paper


# ---- Public: clients ----
def get_data_client() -> Optional[StockHistoricalDataClient]:
    """Return (and memoize) the data client for latest trades."""
    global _ALPACA_DATA_CLIENT
    if _ALPACA_DATA_CLIENT is None:
        k, s, _ = _creds()
        if not k or not s:
            return None
        _ALPACA_DATA_CLIENT = StockHistoricalDataClient(k, s)
    return _ALPACA_DATA_CLIENT


def get_trading_client() -> Optional[TradingClient]:
    """Return (and memoize) the trading client."""
    global _TRADING_CLIENT
    if _TRADING_CLIENT is None:
        k, s, paper = _creds()
        if not k or not s:
            return None
        _TRADING_CLIENT = TradingClient(k, s, paper=paper)
    return _TRADING_CLIENT


# ---- Public: prices ----
def last_trade_price(symbol: str, ttl_sec: int = 10) -> Optional[float]:
    """
    Get latest trade price for a symbol with a tiny cache (ttl_sec).
    Returns float or None if unavailable.
    """
    symbol = (symbol or "").upper().strip()
    if not symbol:
        return None

    now = time.time()
    cached = _PRICE_CACHE.get(symbol)
    if cached and (now - cached[0]) < ttl_sec:
        return cached[1]

    client = get_data_client()
    if client is None:
        return cached[1] if cached else None

    try:
        res = client.get_stock_latest_trade(StockLatestTradeRequest(symbol_or_symbols=symbol))
        trade = res.get(symbol)
        price = float(getattr(trade, "price", None)) if trade else None
        if price is not None:
            _PRICE_CACHE[symbol] = (now, price)
        return price
    except Exception as e:
        logging.getLogger(__name__).warning("ALPACA last price fetch failed for %s: %s", symbol, e)
        return cached[1] if cached else None


def last_trade_prices(symbols: List[str], ttl_sec: int = 10) -> Dict[str, Optional[float]]:
    """Batch get latest prices (cache-aware) for multiple symbols."""
    out: Dict[str, Optional[float]] = {}
    for sym in symbols:
        out[sym] = last_trade_price(sym, ttl_sec=ttl_sec)
    return out


# ---- Public: trading ops ----
def account_summary() -> Optional[Dict[str, Any]]:
    """Return a lightweight account summary dict or None on failure."""
    client = get_trading_client()
    if client is None:
        return None
    try:
        acc = client.get_account()
        return {
            "status": str(getattr(acc, "status", "")),
            "cash": str(getattr(acc, "cash", "")),
            "buying_power": str(getattr(acc, "buying_power", "")),
            "portfolio_value": str(getattr(acc, "portfolio_value", "")),
            "multiplier": str(getattr(acc, "multiplier", "")),
            "pattern_day_trader": bool(getattr(acc, "pattern_day_trader", False)),
            "trading_blocked": bool(getattr(acc, "trading_blocked", False)),
            "transfers_blocked": bool(getattr(acc, "transfers_blocked", False)),
            "account_blocked": bool(getattr(acc, "account_blocked", False)),
            "timestamp": str(getattr(acc, "created_at", "")),
            "env": "paper" if (_creds()[2]) else "live",
        }
    except Exception as e:
        logging.getLogger(__name__).exception("account_summary error")
        return None


def list_positions_slim() -> List[Dict[str, Any]]:
    """
    Return open positions as slim dicts.
    Adds current_price via last_trade_price() when not provided by API.
    """
    client = get_trading_client()
    if client is None:
        return []
    try:
        poss = client.get_all_positions()
        out: List[Dict[str, Any]] = []
        for p in poss:
            sym = getattr(p, "symbol", "")
            cur = getattr(p, "current_price", None)
            if not cur:
                cur = last_trade_price(sym)
            out.append({
                "symbol": sym,
                "qty": getattr(p, "qty", ""),
                "avg_entry_price": getattr(p, "avg_entry_price", ""),
                "current_price": cur if cur is not None else "",
                "unrealized_pl": getattr(p, "unrealized_pl", ""),
                "unrealized_plpc": getattr(p, "unrealized_plpc", ""),
                "side": "long" if float(getattr(p, "qty", "0") or 0) >= 0 else "short",
            })
        return out
    except Exception:
        logging.getLogger(__name__).exception("list_positions_slim error")
        return []


def list_orders(limit: int = 25, status: str = "all") -> List[Dict[str, Any]]:
    """
    List orders using alpaca-py v2 GetOrdersRequest.
    status: 'open'|'closed'|'all'
    """
    client = get_trading_client()
    if client is None:
        return []

    status_map = {
        "open": QueryOrderStatus.OPEN,
        "closed": QueryOrderStatus.CLOSED,
        "all": QueryOrderStatus.ALL,
    }
    qstatus = status_map.get((status or "all").lower(), QueryOrderStatus.ALL)

    try:
        req = GetOrdersRequest(status=qstatus, limit=limit)
        orders = client.get_orders(filter=req)
        out: List[Dict[str, Any]] = []
        for o in orders:
            out.append({
                "id": str(getattr(o, "id", "")),
                "symbol": getattr(o, "symbol", ""),
                "side": getattr(o, "side", ""),
                "qty": getattr(o, "qty", ""),
                "type": getattr(o, "type", ""),
                "time_in_force": getattr(o, "time_in_force", ""),
                "status": getattr(o, "status", ""),
                "submitted_at": str(getattr(o, "submitted_at", "")),
                "filled_qty": getattr(o, "filled_qty", ""),
                "filled_avg_price": getattr(o, "filled_avg_price", ""),
            })
        return out
    except Exception:
        logging.getLogger(__name__).exception("list_orders error")
        return []


def submit_market_order(symbol: str, side: str, qty: int, tif: str = "day") -> Dict[str, Any]:
    """
    Submit a market order.
    side: 'buy'|'sell'
    tif:  'day'|'gtc'|'ioc'|'fok'
    """
    client = get_trading_client()
    if client is None:
        raise RuntimeError("Alpaca TradingClient not initialized")

    side = (side or "buy").lower().strip()
    if side not in ("buy", "sell"):
        raise ValueError("side must be 'buy' or 'sell'")

    tif_map = {
        "day": TimeInForce.DAY,
        "gtc": TimeInForce.GTC,
        "ioc": TimeInForce.IOC,
        "fok": TimeInForce.FOK,
    }
    tif_enum = tif_map.get((tif or "day").lower(), TimeInForce.DAY)

    req = MarketOrderRequest(
        symbol=(symbol or "").upper().strip(),
        qty=str(int(qty)),
        side=OrderSide.BUY if side == "buy" else OrderSide.SELL,
        time_in_force=tif_enum,
    )
    order = client.submit_order(req)
    return {
        "status": "submitted",
        "env": "paper" if (_creds()[2]) else "live",
        "order": {
            "id": str(getattr(order, "id", "")),
            "symbol": getattr(order, "symbol", ""),
            "side": getattr(order, "side", ""),
            "qty": getattr(order, "qty", ""),
            "type": getattr(order, "type", "market"),
            "time_in_force": getattr(order, "time_in_force", tif.upper()),
            "status": getattr(order, "status", "new"),
            "submitted_at": str(getattr(order, "submitted_at", "")),
        },
    }


# ---- Back-compat shims (match names used elsewhere) ----
def _get_trading_client() -> Optional[TradingClient]:
    return get_trading_client()

def _alpaca_last_price(symbol: str, ttl_sec: int = 10) -> Optional[float]:
    return last_trade_price(symbol, ttl_sec=ttl_sec)
