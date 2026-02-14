import { useEffect, useState } from "react";

export function useRegimePolling() {
  const [snapshot, setSnapshot] = useState<any>(null);

  useEffect(() => {
    const fetchSnapshot = async () => {
      try {
        const res = await fetch("http://localhost:5001/regime");

        if (!res.ok) {
          console.error("Polling failed:", res.status);
          return;
        }

        const data = await res.json();

        // 🔎 Debug log (remove later)
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