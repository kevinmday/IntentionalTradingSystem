import { useEffect, useState } from "react"

const API_BASE = "http://127.0.0.1:8001"

async function safeFetch(url: string) {
  try {
    const res = await fetch(url)
    if (!res.ok) return null
    return await res.json()
  } catch {
    return null
  }
}

export function useEnginePolling() {

  const [engineState, setEngineState] = useState<any>(null)
  const [engineStatus, setEngineStatus] = useState<any>(null)
  const [lastDecision, setLastDecision] = useState<any>(null)

  useEffect(() => {

    let polling = false

    const poll = async () => {

      if (polling) return
      polling = true

      try {

        const [status, state, last] = await Promise.all([
          safeFetch(`${API_BASE}/api/engine/status`),
          safeFetch(`${API_BASE}/api/engine/state`),
          safeFetch(`${API_BASE}/api/engine/last`)
        ])

        if (status !== null) setEngineStatus(status)
        if (state !== null) setEngineState(state)
        if (last !== null) setLastDecision(last)

      } catch (err) {

        console.warn("Engine polling error:", err)

      } finally {

        polling = false

      }

    }

    poll()

    const interval = setInterval(poll, 2000)

    return () => clearInterval(interval)

  }, [])

  return {
    engineStatus,
    engineState,
    lastDecision
  }

}