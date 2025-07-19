import os

SIMULATED_ALPACA = os.getenv("SIMULATED_ALPACA", "False").lower() == "true"

def place_order(symbol, qty, side, type="market", time_in_force="gtc"):
    if SIMULATED_ALPACA:
        print(f"[SIMULATED TRADE] {side.upper()} {qty} shares of {symbol}")
        return {
            "status": "simulated",
            "symbol": symbol,
            "qty": qty,
            "side": side,
            "order_id": "SIMULATED_ORDER_001"
        }

    import alpaca_trade_api as tradeapi
    from dotenv import load_dotenv
    load_dotenv()

    API_KEY = os.getenv("APCA_API_KEY_ID")
    SECRET_KEY = os.getenv("APCA_API_SECRET_KEY")
    BASE_URL = os.getenv("APCA_API_BASE_URL", "https://paper-api.alpaca.markets")

    api = tradeapi.REST(API_KEY, SECRET_KEY, BASE_URL, api_version='v2')

    try:
        order = api.submit_order(
            symbol=symbol,
            qty=qty,
            side=side,
            type=type,
            time_in_force=time_in_force
        )
        return {
            "status": order.status,
            "symbol": symbol,
            "qty": qty,
            "side": side,
            "order_id": order.id
        }
    except Exception as e:
        print(f"[Alpaca ERROR] {e}")
        return {"status": "error", "message": str(e)}

