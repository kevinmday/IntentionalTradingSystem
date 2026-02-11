from dataclasses import dataclass


@dataclass(frozen=True)
class Position:
    """
    Immutable representation of a single open position.
    """

    symbol: str
    quantity: float
    average_entry_price: float

    market_value: float
    unrealized_pnl: float

    side: str  # "long" / "short"
