import { useEffect, useState } from "react";
import { fetchRegime } from "../api/regime";
import type { RegimeSnapshot } from "../api/regime";

export function useRegime(pollInterval = 1500) {
  const [data, setData] = useState<RegimeSnapshot | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isOnline, setIsOnline] = useState(true);

  useEffect(() => {
    let mounted = true;

    async function poll() {
      try {
        const snapshot = await fetchRegime();
        if (mounted) {
          setData(snapshot);
          setError(null);
          setIsOnline(true);
        }
      } catch (err: any) {
        if (mounted) {
          setError(err.message);
          setIsOnline(false);
        }
      }
    }

    poll();
    const interval = setInterval(poll, pollInterval);

    return () => {
      mounted = false;
      clearInterval(interval);
    };
  }, [pollInterval]);

  return { data, error, isOnline };
}
