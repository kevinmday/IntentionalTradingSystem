import React, { useEffect, useState } from "react";

type Snapshot = {
  sector_avg: number;
  prime_avg: number;
  breadth: number;
  etf_confirmation: boolean;
  pullback_depth: number;
  volume_delta: number;
  timestamp: string;
};

function valueColor(value: number) {
  if (value > 0) return "text-emerald-400";
  if (value < 0) return "text-red-400";
  return "text-neutral-400";
}

export default function PropagationPanel() {
  const [snapshot, setSnapshot] = useState<Snapshot | null>(null);
  const [log, setLog] = useState<any[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setError(null);

        // 🔥 PROXY-BASED CALL (NO CORS)
        const res = await fetch("/api/propagation_snapshot");

        if (!res.ok) {
          const txt = await res.text();
          throw new Error(`HTTP ${res.status}: ${txt}`);
        }

        const data = (await res.json()) as Snapshot;
        setSnapshot(data);
      } catch (err: any) {
        setError(err?.message ?? String(err));
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 2000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (!snapshot) return;

    setLog((prev) => {
      const updated = [
        {
          time: new Date(snapshot.timestamp).toLocaleTimeString(),
          sector: snapshot.sector_avg,
          breadth: snapshot.breadth,
          etf: snapshot.etf_confirmation,
        },
        ...prev,
      ];

      return updated.slice(0, 25);
    });
  }, [snapshot]);

  if (error) {
    return (
      <div className="p-6 text-sm font-mono space-y-3">
        <div className="text-neutral-400 tracking-widest">
          PROPAGATION OBSERVATORY
        </div>
        <div className="text-red-400">FETCH ERROR</div>
        <pre className="text-xs text-neutral-200 whitespace-pre-wrap break-words border border-neutral-800 p-3 rounded">
          {error}
        </pre>
      </div>
    );
  }

  if (!snapshot) {
    return (
      <div className="p-6 text-neutral-400 text-sm font-mono">
        Loading propagation telemetry...
      </div>
    );
  }

  return (
    <div className="p-6 text-sm font-mono space-y-6">
      <div className="text-neutral-400 tracking-widest">
        PROPAGATION OBSERVATORY
      </div>

      <div className="space-y-2">
        <div>
          Sector Avg:
          <span className={valueColor(snapshot.sector_avg)}>
            {" "}{snapshot.sector_avg}%
          </span>
        </div>

        <div>
          Prime Avg:
          <span className={valueColor(snapshot.prime_avg)}>
            {" "}{snapshot.prime_avg}%
          </span>
        </div>

        <div>
          Breadth:
          <span className="text-neutral-200">
            {" "}{snapshot.breadth}
          </span>
        </div>

        <div>
          ETF Confirmation:
          <span
            className={
              snapshot.etf_confirmation
                ? "text-emerald-400"
                : "text-red-400"
            }
          >
            {" "}{snapshot.etf_confirmation ? "YES" : "NO"}
          </span>
        </div>

        <div>
          Pullback Depth:
          <span className={valueColor(snapshot.pullback_depth)}>
            {" "}{snapshot.pullback_depth}%
          </span>
        </div>

        <div>
          Volume Delta:
          <span className={valueColor(snapshot.volume_delta)}>
            {" "}{snapshot.volume_delta}%
          </span>
        </div>
      </div>

      <div className="border-t border-neutral-800 pt-4 space-y-2">
        <div className="text-neutral-400">Ripple Log</div>

        <div className="space-y-1 text-xs max-h-64 overflow-y-auto">
          {log.map((entry, idx) => (
            <div key={idx}>
              {entry.time} | sector {entry.sector}% | breadth {entry.breadth} | etf{" "}
              {entry.etf ? "T" : "F"}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}