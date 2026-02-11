from dataclasses import dataclass


@dataclass(frozen=True)
class OrderIntent:
    """
    Immutable execution intent emitted by ExecutionEngine.

    This does NOT execute orders.
    It only expresses what should happen.
    """

    symbol: str
    side: str          # "buy" / "sell"
    order_type: str    # "market" / "limit"
    quantity: float
    rationale: str
    confidence: float
