"""
MarketMind Data Provider Registry

Controls which market data provider the engine uses.

Providers supported:
- stub (default)
- alpaca

Selection is controlled via environment variable:

    MARKETMIND_DATA_PROVIDER=alpaca
"""

import os

from marketmind_engine.data.stub import StubDataProvider


# ---------------------------------------------------------
# Optional Alpaca provider
# ---------------------------------------------------------

try:
    from marketmind_engine.broker.alpaca_paper_adapter import AlpacaPaperBrokerAdapter
except Exception:
    AlpacaPaperBrokerAdapter = None


# ---------------------------------------------------------
# Active Provider
# ---------------------------------------------------------

_PROVIDER_NAME = os.getenv("MARKETMIND_DATA_PROVIDER", "stub").lower()

if _PROVIDER_NAME == "alpaca" and AlpacaPaperBrokerAdapter is not None:

    _ACTIVE_PROVIDER = AlpacaPaperBrokerAdapter()

else:

    _ACTIVE_PROVIDER = StubDataProvider()


# ---------------------------------------------------------
# Provider Access
# ---------------------------------------------------------

def get_provider():
    """
    Returns the currently active data provider.
    """
    return _ACTIVE_PROVIDER


def set_provider(provider):
    """
    Allows runtime provider override.
    """
    global _ACTIVE_PROVIDER
    _ACTIVE_PROVIDER = provider


def get_provider_name():
    """
    Returns name of the active provider.
    """
    return _ACTIVE_PROVIDER.__class__.__name__
