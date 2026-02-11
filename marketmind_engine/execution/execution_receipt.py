from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class ExecutionReceipt:
    """
    Immutable result returned from a broker adapter.

    This represents submission acknowledgement,
    not a fill report.
    """

    broker_name: str
    symbol: str
    side: str
    quantity: float
    order_type: str

    broker_order_id: Optional[str]
    accepted: bool
    message: Optional[str]

    timestamp_utc: datetime
