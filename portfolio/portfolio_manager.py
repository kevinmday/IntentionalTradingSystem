from dataclasses import dataclass
from typing import Dict

from marketmind_engine.execution.capital_snapshot import CapitalSnapshot
from marketmind_engine.execution.position import Position
from marketmind_engine.execution.position_snapshot import PositionSnapshot
from marketmind_engine.execution.execution_receipt import ExecutionReceipt


@dataclass
class PortfolioState:
    capital: CapitalSnapshot
    positions: Dict[str, Position]


class PortfolioManager:
    """
    Authoritative portfolio mutation engine.
    """

    def __init__(self, initial_capital: CapitalSnapshot):
        self._capital = initial_capital
        self._positions: Dict[str, Position] = {}

    # ---------------------------------------------------------
    # APPLY EXECUTION (OPEN POSITION)
    # ---------------------------------------------------------

    def apply_execution(self, receipt: ExecutionReceipt, price: float) -> None:

        if not receipt.accepted:
            return

        symbol = receipt.symbol
        quantity = receipt.quantity
        side = receipt.side

        notional = quantity * price

        # --- Update Capital ---
        new_cash = self._capital.cash - notional
        new_exposure = self._capital.total_exposure + notional

        self._capital = CapitalSnapshot(
            account_equity=self._capital.account_equity,
            buying_power=self._capital.buying_power - notional,
            cash=new_cash,
            total_exposure=new_exposure,
            max_risk_per_trade=self._capital.max_risk_per_trade,
            open_positions_count=len(self._positions) + 1,
            margin_enabled=self._capital.margin_enabled,
        )

        # --- Create Position ---
        self._positions[symbol] = Position(
            symbol=symbol,
            quantity=quantity,
            average_entry_price=price,
            market_value=notional,
            unrealized_pnl=0.0,
            side="long" if side == "buy" else "short",
        )

    # ---------------------------------------------------------
    # CLOSE POSITION (FULL EXIT)
    # ---------------------------------------------------------

    def close_position(self, symbol: str, price: float) -> None:

        position = self._positions.get(symbol)
        if position is None:
            return

        exit_value = position.quantity * price
        entry_value = position.quantity * position.average_entry_price

        realized_pnl = exit_value - entry_value

        new_cash = self._capital.cash + exit_value
        new_exposure = self._capital.total_exposure - position.market_value
        new_equity = new_cash  # no remaining exposure for this symbol

        del self._positions[symbol]

        self._capital = CapitalSnapshot(
            account_equity=new_equity,
            buying_power=self._capital.buying_power + exit_value,
            cash=new_cash,
            total_exposure=new_exposure,
            max_risk_per_trade=self._capital.max_risk_per_trade,
            open_positions_count=len(self._positions),
            margin_enabled=self._capital.margin_enabled,
        )

    # ---------------------------------------------------------
    # MARK TO MARKET
    # ---------------------------------------------------------

    def update_mark_to_market(self, price_map: Dict[str, float]) -> None:

        updated_positions: Dict[str, Position] = {}

        total_market_value = 0.0
        total_unrealized_pnl = 0.0

        for symbol, position in self._positions.items():

            current_price = price_map.get(symbol)

            if current_price is None:
                updated_positions[symbol] = position
                total_market_value += position.market_value
                total_unrealized_pnl += position.unrealized_pnl
                continue

            new_market_value = position.quantity * current_price
            new_unrealized = (
                (current_price - position.average_entry_price)
                * position.quantity
            )

            updated_position = Position(
                symbol=position.symbol,
                quantity=position.quantity,
                average_entry_price=position.average_entry_price,
                market_value=new_market_value,
                unrealized_pnl=new_unrealized,
                side=position.side,
            )

            updated_positions[symbol] = updated_position

            total_market_value += new_market_value
            total_unrealized_pnl += new_unrealized

        self._positions = updated_positions

        new_equity = self._capital.cash + total_market_value

        self._capital = CapitalSnapshot(
            account_equity=new_equity,
            buying_power=self._capital.buying_power,
            cash=self._capital.cash,
            total_exposure=total_market_value,
            max_risk_per_trade=self._capital.max_risk_per_trade,
            open_positions_count=len(self._positions),
            margin_enabled=self._capital.margin_enabled,
        )

    # ---------------------------------------------------------
    # SNAPSHOTS
    # ---------------------------------------------------------

    def capital_snapshot(self) -> CapitalSnapshot:
        return self._capital

    def position_snapshot(self) -> PositionSnapshot:

        total_value = sum(p.market_value for p in self._positions.values())
        total_pnl = sum(p.unrealized_pnl for p in self._positions.values())

        return PositionSnapshot(
            positions=self._positions.copy(),
            total_market_value=total_value,
            total_unrealized_pnl=total_pnl,
        )