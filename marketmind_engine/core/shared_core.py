# shared_core.py
# Neutral place for shared imports to avoid circular dependencies

from marketmind_engine.analysis.quant.indicators import fetch_technical_indicators
from marketmind_engine.intention.engine import generate_trade_metrics

# These will be initialized in main
AGENT = None

# Optionally placeholder functions so routes won't break
def get_daily_stock_data(*args, **kwargs):
    raise NotImplementedError("get_daily_stock_data not yet bound")

def calculate_metrics(*args, **kwargs):
    raise NotImplementedError("calculate_metrics not yet bound")
