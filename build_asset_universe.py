import os
import sqlite3
from dotenv import load_dotenv
from alpaca.trading.client import TradingClient

# --- LOAD ENV (force override to avoid OS shadowing) ---
load_dotenv(override=True)

# --- CONFIG ---
DB_NAME = "asset_universe.db"

# --- CONNECT TO ALPACA ---
api_key = os.getenv("APCA_API_KEY_ID")
api_secret = os.getenv("APCA_API_SECRET_KEY")

if not api_key or not api_secret:
    raise ValueError("Alpaca API keys not found in environment variables.")

client = TradingClient(api_key, api_secret, paper=True)

print("Pulling tradable assets from Alpaca...")

# --- RAW JSON REQUEST (bypass strict Asset model validation) ---
assets = client.get("/assets")

print(f"Total assets received: {len(assets)}")

# --- FILTER TRADABLE US EQUITIES ---
tradable_assets = [
    a for a in assets
    if a.get("tradable")
    and a.get("status") == "active"
    and a.get("class") == "us_equity"
]

print(f"Tradable US equities: {len(tradable_assets)}")

# --- CREATE DATABASE ---
conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS assets (
    symbol TEXT PRIMARY KEY,
    name TEXT,
    asset_class TEXT,
    exchange TEXT,
    status TEXT,
    tradable BOOLEAN,
    marginable BOOLEAN,
    shortable BOOLEAN,
    easy_to_borrow BOOLEAN
)
""")

# --- INSERT DATA ---
for asset in tradable_assets:
    cursor.execute("""
        INSERT OR REPLACE INTO assets VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        asset.get("symbol"),
        asset.get("name"),
        asset.get("class"),
        asset.get("exchange"),
        asset.get("status"),
        int(asset.get("tradable", False)),
        int(asset.get("marginable", False)),
        int(asset.get("shortable", False)),
        int(asset.get("easy_to_borrow", False))
    ))

conn.commit()
conn.close()

print("Asset universe database created successfully.")
print(f"Database: {DB_NAME}")