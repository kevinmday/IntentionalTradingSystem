from dataclasses import dataclass


@dataclass(frozen=True)
class CapitalSnapshot:
    """
    Immutable view of account capital state.

    Provided to ExecutionEngine to determine position sizing.
    """

    account_equity: float
    buying_power: float
    cash: float

    total_exposure: float

    max_risk_per_trade: float  # fraction of equity (e.g. 0.01 = 1%)

    open_positions_count: int

    margin_enabled: bool
