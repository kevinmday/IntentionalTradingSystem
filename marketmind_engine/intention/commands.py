import requests
# marketmind/intention_commands.py

from .rss_parser import parse_default_rss
from .intention_engine import evaluate_fils_ucip_ttcfs
from .trade_logic import generate_trade_cards, queue_trades

def get_quant_metrics(ticker):
    try:
        api_key = "8a55e1b9d3904a77b29466e1409ed23f"
        base_url = "https://api.twelvedata.com"
        params = {
            "symbol": ticker,
            "interval": "1day",
            "apikey": api_key,
            "outputsize": 100
        }

        resp = requests.get(f"{base_url}/time_series", params=params)
        data = resp.json()

        if "values" not in data or not data["values"]:
            print(f"[Quant Fetch Error] No 'values' for {ticker}: {data}")
            return {}

        latest = data["values"][0]
        price = float(latest.get("close", 0))
        volume = int(float(latest.get("volume", 0)))

        def get_indicator(indicator, time_period):
            try:
                r = requests.get(f"{base_url}/{indicator}", params={
                    "symbol": ticker,
                    "interval": "1day",
                    "time_period": time_period,
                    "apikey": api_key
                })
                d = r.json()

                key_map = {
                    "sma": "sma",
                    "ema": "ema",
                    "rsi": "rsi"
                }

                key = key_map.get(indicator.lower())
                if 'values' in d and isinstance(d['values'], list) and key in d['values'][0]:
                    return float(d['values'][0][key])
                else:
                    print(f"[{indicator.upper()} Fetch Error] {d}")
                    return None

            except Exception as e:
                print(f"[{indicator.upper()} Fetch Error] {e}")
                return None

        sma50 = get_indicator("sma", 50)
        sma200 = get_indicator("sma", 200)
        ema20 = get_indicator("ema", 20)
        rsi = get_indicator("rsi", 14)

        return {
            "Price": round(price, 2),
            "Volume": volume,
            "SMA50": round(sma50, 2) if sma50 is not None else None,
            "SMA200": round(sma200, 2) if sma200 is not None else None,
            "EMA20": round(ema20, 2) if ema20 is not None else None,
            "RSI": round(rsi, 2) if rsi is not None else None,
            "MACD": "n/a"
        }

    except Exception as e:
        print(f"[Quant Fetch Error] {e}")
        return {}

def run_default_scan():
    scan_data = parse_default_rss()
    return scan_data

def generate_trade_cards_from_scan(scan_data):
    metrics = evaluate_fils_ucip_ttcfs(scan_data)
    trade_cards = generate_trade_cards(metrics)
    return trade_cards

def queue_top_trades(trade_cards, threshold=0.05):
    queued = queue_trades([t for t in trade_cards if t.get('alpha_score', 0) > threshold])
    return queued

