from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class MarketBar:
    """
    Canonical market bar contract.

    This represents a COMPLETED bar only.
    No partial bars. No provider-specific fields.

    All timestamps MUST be UTC and represent bar CLOSE time.
    """

    timestamp: datetime        # bar close time (UTC)
    volume: float              # total volume in bar
    trade_count: int           # number of trades in bar

    def validate(self) -> None:
        """
        Defensive validation for replay / ingestion.
        Raises ValueError on invalid bar.
        """
        if self.volume < 0:
            raise ValueError("MarketBar.volume must be >= 0")

        if self.trade_count < 0:
            raise ValueError("MarketBar.trade_count must be >= 0")

        if self.timestamp.tzinfo is None:
            raise ValueError("MarketBar.timestamp must be timezone-aware (UTC)")

    @classmethod
    def from_mapping(cls, data: dict[str, Any]) -> "MarketBar":
        """
        Helper constructor for CSV / JSON ingestion layers.
        Expects keys: timestamp, volume, trade_count
        """
        bar = cls(
            timestamp=data["timestamp"],
            volume=float(data["volume"]),
            trade_count=int(data["trade_count"]),
        )
        bar.validate()
        return bar