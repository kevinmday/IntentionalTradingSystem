import { useEffect, useState } from "react";

export function useRegimePolling() {
  const [snapshot, setSnapshot] = useState<any>(null);

  useEffect(() => {
    const fetchSnapshot = async () => {
      try {

        // Use Vite proxy when available
        const res = await fetch("/api/engine/status");

        // If proxy not configured, fallback to direct backend
        if (!res.ok) {
          const fallback = await fetch("http://localhost:8001/api/engine/status");

          if (!fallback.ok) {
            console.error("Polling failed:", fallback.status);
            return;
          }

          const data = await fallback.json();
          console.log("REGIME PAYLOAD:", data);
          setSnapshot(data);
          return;
        }

        const data = await res.json();

        // Debug log
        console.log("REGIME PAYLOAD:", data);

        setSnapshot(data);

      } catch (err) {
        console.error("Polling error:", err);
      }
    };

    fetchSnapshot();

    const interval = setInterval(fetchSnapshot, 1500);

    return () => clearInterval(interval);

  }, []);

  return { snapshot };
}