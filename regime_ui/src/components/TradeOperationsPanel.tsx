import React, { useState } from "react"
import { useEnginePolling } from "../hooks/useEnginePolling"

export default function TradeOperationsPanel() {

  const [loading, setLoading] = useState(false)
  const [engineResult, setEngineResult] = useState<any>(null)

  const { engineStatus, engineState, lastDecision } = useEnginePolling()

  const mockPositions = [
    { symbol: "NVDA", pnl: "+2.3%", drift: "0.028" },
    { symbol: "PLTR", pnl: "+1.1%", drift: "0.022" },
    { symbol: "SMCI", pnl: "-0.4%", drift: "0.011" }
  ]

  // ================= ENGINE CONTROL =================

  const startEngine = async () => {

    try {

      const res = await fetch(
        "http://127.0.0.1:8001/api/engine/start",
        { method: "POST" }
      )

      const data = await res.json()
      setEngineResult(data)

    } catch (err) {

      console.error("Engine start failed", err)

      setEngineResult({
        decision: "ERROR",
        reason: "Engine start failed"
      })

    }

  }

  const stopEngine = async () => {

    try {

      const res = await fetch(
        "http://127.0.0.1:8001/api/engine/stop",
        { method: "POST" }
      )

      const data = await res.json()
      setEngineResult(data)

    } catch (err) {

      console.error("Engine stop failed", err)

      setEngineResult({
        decision: "ERROR",
        reason: "Engine stop failed"
      })

    }

  }

  const runCycle = async () => {

    setLoading(true)

    try {

      const response = await fetch(
        "http://127.0.0.1:8001/api/engine/run",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({
            symbol: "NVDA"
          })
        }
      )

      const data = await response.json()
      setEngineResult(data)

    } catch (err) {

      console.error("Trade execution failed", err)

      setEngineResult({
        decision: "ERROR",
        reason: "API call failed"
      })

    }

    setLoading(false)

  }

  return (
    <div className="panel">

      <h2 className="panel-title">TRADE OPERATIONS</h2>

      {/* ================= ENGINE STATUS ================= */}

      <div className="trade-section">

        <h3>Engine Status</h3>

        <div>Running: {engineStatus?.running ? "YES" : "NO"}</div>

        <div>
          Regime: {engineState?.regime?.regime ?? "--"}
        </div>

        <div>
          Composite Score: {engineState?.regime?.composite_score ?? "--"}
        </div>

        <div>
          Engine Time: {engineState?.engine_time ?? "--"}
        </div>

      </div>

      {/* ================= LAST ENGINE DECISION ================= */}

      <div className="trade-section">

        <h3>Last Engine Decision</h3>

        <div>
          Symbol: {lastDecision?.symbol ?? "--"}
        </div>

        <div>
          Decision: {lastDecision?.decision ?? "--"}
        </div>

        <div>
          Engine Time: {lastDecision?.engine_time ?? "--"}
        </div>

        <div>
          Reason: {lastDecision?.reason ?? "--"}
        </div>

      </div>

      {/* ================= ENGINE CONTROL ================= */}

      <div className="trade-section">

        <h3>Engine Control</h3>

        <div style={{ display: "flex", gap: "10px" }}>

          <button
            className="trade-button"
            onClick={startEngine}
          >
            START ENGINE
          </button>

          <button
            className="trade-button"
            onClick={runCycle}
            disabled={loading}
          >
            {loading ? "RUNNING..." : "RUN CYCLE"}
          </button>

          <button
            className="trade-button"
            onClick={stopEngine}
          >
            STOP ENGINE
          </button>

        </div>

      </div>

      {/* ================= TRADE CARD ================= */}

      <div className="trade-section">

        <h3>Trade Card</h3>

        <div className="trade-card">

          <div>Ticker: NVDA</div>
          <div>Signal: BUY</div>
          <div>PsiQuant: 83</div>
          <div>Drift: 0.031</div>
          <div>Entry: $912.40</div>
          <div>Stop: $895.20</div>
          <div>Target: $945.00</div>

          <button
            className="trade-button"
            onClick={runCycle}
            disabled={loading}
          >
            {loading ? "EXECUTING..." : "EXECUTE TRADE"}
          </button>

        </div>

      </div>

      {/* ================= ACTIVE POSITIONS ================= */}

      <div className="trade-section">

        <h3>Active Positions</h3>

        {mockPositions.map(p => (
          <div key={p.symbol} className="position-row">
            <span>{p.symbol}</span>
            <span>{p.pnl}</span>
            <span>Drift {p.drift}</span>
          </div>
        ))}

      </div>

      {/* ================= EXIT MONITOR ================= */}

      <div className="trade-section">

        <h3>Exit Monitor</h3>

        <div className="exit-alert">
          NVDA drift weakening — lock 60%
        </div>

      </div>

      {/* ================= CAPITAL STATUS ================= */}

      <div className="trade-section">

        <h3>Capital Status</h3>

        <div>Total Capital: $13,723</div>
        <div>Allocated: $10,900</div>
        <div>Cash: $2,823</div>

      </div>

    </div>
  )
}