from collections import deque
from datetime import datetime
from typing import Iterable, List

from marketmind_engine.data.bars import MarketBar
from marketmind_engine.adapters.liquidity_adapter import LiquidityAdapter
from marketmind_engine.decision.decision_engine import DecisionEngine
from marketmind_engine.decision.state import MarketState
from marketmind_engine.analysis.metric_shim_phase3 import (
    derive_metrics_phase3_shim,
)


class ReplayResult:
    """
    Lightweight container for replay outcomes.
    No P&L. No orders. Observation only.
    """

    def __init__(self):
        self.decisions: List[str] = []
        self.timestamps: List[datetime] = []


def run_replay(
    *,
    bars: Iterable[MarketBar],
    liquidity_adapter: LiquidityAdapter,
    decision_engine: DecisionEngine,
    symbol: str,
    window_size: int,
) -> ReplayResult:
    """
    Replays a sequence of COMPLETED bars through the engine.

    - Maintains rolling volume / trade windows
    - Evaluates liquidity adapter
    - Derives placeholder metrics (PHASE-3 SHIM)
    - Builds MarketState
    - Calls DecisionEngine.evaluate(state)

    No trading. No execution. No side effects.
    """

    volumes = deque(maxlen=window_size)
    trades = deque(maxlen=window_size)

    result = ReplayResult()

    for bar in bars:
        bar.validate()

        volumes.append(bar.volume)
        trades.append(bar.trade_count)

        liquidity_ctx = liquidity_adapter.evaluate(
            volume_series=list(volumes),
            trade_count_series=list(trades),
            now=bar.timestamp,
            symbol=symbol,
        )

        # --- PHASE-3 TEMP METRIC SHIM ---
        ucip, fils, ttcf = derive_metrics_phase3_shim(liquidity_ctx)

        state = MarketState(
            ucip=ucip,
            fils=fils,
            ttcf=ttcf,
            symbol=symbol,
            data_source="replay",
            timestamp_utc=bar.timestamp.isoformat(),
        )

        decision = decision_engine.evaluate(state)

        result.decisions.append(decision.decision)
        result.timestamps.append(bar.timestamp)

    return result