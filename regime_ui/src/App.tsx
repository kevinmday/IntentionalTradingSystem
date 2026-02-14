import React, { useEffect, useState } from "react";
import { RegimeIndicator } from "./components/RegimeIndicator";
import { FlattenFlagIndicator } from "./components/FlattenFlagIndicator";
import { EntryBlockIndicator } from "./components/EntryBlockIndicator";
import { useRegimePolling } from "./hooks/useRegimePolling";

function App() {
  const { snapshot } = useRegimePolling();

  const regime = snapshot?.regime ?? "unknown";
  const flatten = snapshot?.flatten ?? false;
  const block = snapshot?.entry_block ?? false;
  const updated = snapshot?.timestamp
    ? new Date(snapshot.timestamp).toLocaleTimeString()
    : "--:--:--";

  const systemic = regime === "systemic";

  // Phase 11.3B — Duration Counter
  const [regimeStartTime, setRegimeStartTime] = useState<number | null>(null);
  const [previousRegime, setPreviousRegime] = useState<string | null>(null);
  const [, forceTick] = useState(0);

  useEffect(() => {
    if (!snapshot?.regime) return;

    if (snapshot.regime !== previousRegime) {
      setPreviousRegime(snapshot.regime);
      setRegimeStartTime(Date.now());
    }
  }, [snapshot?.regime]);

  useEffect(() => {
    const interval = setInterval(() => {
      forceTick((x) => x + 1);
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  const getDuration = () => {
    if (!regimeStartTime) return "00:00:00";

    const seconds = Math.floor((Date.now() - regimeStartTime) / 1000);

    const hrs = String(Math.floor(seconds / 3600)).padStart(2, "0");
    const mins = String(Math.floor((seconds % 3600) / 60)).padStart(2, "0");
    const secs = String(seconds % 60).padStart(2, "0");

    return ${hrs}::;
  };

  return (
    <div
      className={min-h-screen text-white font-mono }
    >
      <div className="border-b border-gray-800 px-4 py-2 text-sm flex justify-between">
        <div className="flex gap-6">
          <span>REGIME: {regime.toUpperCase()}</span>
          <span>FLATTEN: {flatten ? "YES" : "NO"}</span>
          <span>BLOCK: {block ? "YES" : "NO"}</span>
        </div>
        <div>UPDATED: {updated}</div>
      </div>

      <div className="px-6 py-4 text-xs text-gray-400">
        TIME IN CURRENT STATE: {getDuration()}
      </div>

      <div className="px-6 py-4 space-y-4">
        <RegimeIndicator regime={regime} />
        <FlattenFlagIndicator flatten={flatten} />
        <EntryBlockIndicator block={block} />
      </div>
    </div>
  );
}

export default App;
