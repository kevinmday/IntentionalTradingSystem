"""
Replay Position Service

Maintains deterministic in-memory position state
for replay simulations.

Replay-only.
Conforms to real PositionSnapshot contract.
Does NOT modify core engine logic.
"""

from typing import Dict

from marketmind_engine.execution.position_snapshot import PositionSnapshot
from marketmind_engine.execution.position import Position


class ReplayPositionService:
    """
    Tracks real Position objects by symbol.
    """

    def __init__(self):
        self._positions: Dict[str, Position] = {}

    # --------------------------------------------------
    # Snapshot (Engine-Compatible)
    # --------------------------------------------------

    def snapshot(self, symbol: str) -> PositionSnapshot:
        """
        Return a real PositionSnapshot object
        matching engine expectations.
        """

        total_market_value = sum(
            p.market_value for p in self._positions.values()
        )

        total_unrealized_pnl = sum(
            p.unrealized_pnl for p in self._positions.values()
        )

        return PositionSnapshot(
            positions=dict(self._positions),
            total_market_value=total_market_value,
            total_unrealized_pnl=total_unrealized_pnl,
        )

    # --------------------------------------------------
    # Fill Application
    # --------------------------------------------------

    def apply_fill(
        self,
        symbol: str,
        side: str,
        quantity: float,
        price: float,
    ):
        """
        Apply execution fills into replay state.

        Uses real Position objects.
        """

        if side == "buy":

            if symbol in self._positions:
                existing = self._positions[symbol]

                new_qty = existing.quantity + quantity

                new_avg = (
                    (existing.quantity * existing.average_entry_price)
                    + (quantity * price)
                ) / new_qty
            else:
                new_qty = quantity
                new_avg = price

            market_value = new_qty * price
            unrealized_pnl = (price - new_avg) * new_qty

            self._positions[symbol] = Position(
                symbol=symbol,
                quantity=new_qty,
                average_entry_price=new_avg,
                market_value=market_value,
                unrealized_pnl=unrealized_pnl,
                side="long",
            )

        elif side == "sell":

            existing = self._positions.get(symbol)
            if not existing:
                return

            new_qty = existing.quantity - quantity

            if new_qty <= 0:
                self._positions.pop(symbol, None)
                return

            market_value = new_qty * price
            unrealized_pnl = (
                price - existing.average_entry_price
            ) * new_qty

            self._positions[symbol] = Position(
                symbol=symbol,
                quantity=new_qty,
                average_entry_price=existing.average_entry_price,
                market_value=market_value,
                unrealized_pnl=unrealized_pnl,
                side="long",
            )