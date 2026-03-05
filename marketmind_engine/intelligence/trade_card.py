"""
MarketMind — Live Trade Card Generator

LIVE PIPELINE

RSS feeds
→ Symbol Discovery
→ Alpaca Market Data
→ Trade Candidate Scoring
→ Trade Card

NO SIMULATION
NO YFINANCE
LIVE MARKET DATA ONLY
"""

import os
from datetime import datetime, UTC

from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockLatestQuoteRequest

from marketmind_engine.intelligence.symbol_discovery import discover


# --------------------------------------------------
# Alpaca Configuration
# --------------------------------------------------

API_KEY = os.getenv("APCA_API_KEY_ID")
API_SECRET = os.getenv("APCA_API_SECRET_KEY")

if not API_KEY or not API_SECRET:
    raise RuntimeError("Alpaca API keys not found in environment variables")


client = StockHistoricalDataClient(API_KEY, API_SECRET)


# --------------------------------------------------
# Market Data Lookup (LIVE)
# --------------------------------------------------

def get_price(symbol):

    try:

        req = StockLatestQuoteRequest(symbol_or_symbols=[symbol])

        quote = client.get_stock_latest_quote(req)

        q = quote.get(symbol)

        if not q:
            return None

        # Prefer ask price if available
        if q.ask_price and q.ask_price > 0:
            return float(q.ask_price)

        if q.bid_price and q.bid_price > 0:
            return float(q.bid_price)

        return None

    except Exception as e:

        print(f"Price lookup failed for {symbol}: {e}")
        return None


# --------------------------------------------------
# Trade Scoring
# --------------------------------------------------

def score_symbol(price):

    """
    Simple ranking model for now.
    Will later incorporate:

    FILS
    UCIP
    TTCF
    Drift
    narrative acceleration
    """

    if price < 10:
        return 0.6

    elif price < 50:
        return 0.8

    else:
        return 0.7


# --------------------------------------------------
# Trade Card Generator
# --------------------------------------------------

def generate_trade_card():

    print("\n=== MARKETMIND TRADE CARD ===\n")

    symbols = discover(return_symbols=True)

    if not symbols:
        print("No symbols discovered")
        return


    candidates = []


    for sym in symbols:

        price = get_price(sym)

        if not price:
            continue

        score = score_symbol(price)

        candidates.append({
            "symbol": sym,
            "price": round(price, 2),
            "score": score
        })


    candidates.sort(key=lambda x: x["score"], reverse=True)


    print("Rank  Symbol  Price   Score\n")


    for i, c in enumerate(candidates, 1):

        print(
            f"{i:<5} {c['symbol']:<6} ${c['price']:<7} {c['score']}"
        )


    print("\nGenerated:", datetime.now(UTC))


# --------------------------------------------------
# Runner
# --------------------------------------------------

def run():

    generate_trade_card()


if __name__ == "__main__":

    run()