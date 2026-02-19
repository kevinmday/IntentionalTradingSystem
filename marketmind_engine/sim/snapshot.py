class SimulatedPositionSnapshot:
    """
    Minimal deterministic snapshot for lifecycle evaluation.

    Only contains fields required for lifecycle EXIT logic testing.
    """

    def __init__(self, symbol: str, entry_price: float, current_price: float):
        self.symbol = symbol
        self.entry_price = entry_price
        self.current_price = current_price

    @property
    def pnl_pct(self) -> float:
        return (self.current_price - self.entry_price) / self.entry_price
