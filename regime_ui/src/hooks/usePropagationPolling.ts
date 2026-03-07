import { useEffect, useState } from "react"

export function usePropagationPolling() {

  const [snapshot, setSnapshot] = useState<any>(null)

  useEffect(() => {

    const fetchData = async () => {

      try {

        const res = await fetch(
          "http://127.0.0.1:8001/api/propagation_snapshot"
        )

        const json = await res.json()

        setSnapshot(json)

      } catch (err) {
        console.error("Propagation polling error:", err)
      }

    }

    fetchData()

    const interval = setInterval(fetchData, 2000)

    return () => clearInterval(interval)

  }, [])

  return snapshot
}