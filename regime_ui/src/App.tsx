import React, { useEffect, useState } from "react";
import RegimeIndicator from "./components/RegimeIndicator";
import FlattenFlagIndicator from "./components/FlattenFlagIndicator";
import EntryBlockIndicator from "./components/EntryBlockIndicator";
import { useRegimePolling } from "./hooks/useRegimePolling";

type TransitionEntry = {
  regime: string;
  time: string;
};

function App() {
  const { snapshot } = useRegimePolling();

  const regime = snapshot?.regime ?? "unknown";
  const flatten = snapshot?.flatten_triggered ?? false;
  const block = snapshot?.block_new_entries ?? false;

  const updated = snapshot?.timestamp
    ? new Date(snapshot.timestamp * 1000).toLocaleTimeString()
    : "--:--:--";

  const systemic = regime === "systemic";

  // -----------------------------
  // Duration Counter
  // -----------------------------

  const [regimeStartTime, setRegimeStartTime] = useState<number | null>(null);
  const [previousRegime, setPreviousRegime] = useState<string | null>(null);
  const [, forceTick] = useState(0);

  useEffect(() => {
    if (!snapshot?.regime) return;

    if (snapshot.regime !== previousRegime) {
      setPreviousRegime(snapshot.regime);
      setRegimeStartTime(Date.now());
      addTransition(snapshot.regime);
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

    return `${hrs}:${mins}:${secs}`;
  };

  // -----------------------------
  // Transition Ring Buffer
  // -----------------------------

  const [transitions, setTransitions] = useState<TransitionEntry[]>([]);

  const addTransition = (newRegime: string) => {
    const entry: TransitionEntry = {
      regime: newRegime.toUpperCase(),
      time: new Date().toLocaleTimeString(),
    };

    setTransitions((prev) => {
      const updated = [entry, ...prev];
      return updated.slice(0, 10);
    });
  };

  // -----------------------------
  // Render
  // -----------------------------

  return (
    <div
      className={`min-h-screen font-mono text-sm ${
        systemic ? "bg-red-950 text-red-200" : "bg-black text-green-400"
      }`}
    >
      {/* Terminal Status Strip */}
      <div className="border-b border-gray-800 px-4 py-2 tracking-wider">
        REGIME:{regime.toUpperCase()} | FLATTEN:{flatten ? "YES" : "NO"} | BLOCK:
        {block ? "YES" : "NO"} | UPDATED:{updated}
      </div>

      {/* Duration */}
      <div className="px-4 py-2 text-gray-500">
        TIME_IN_STATE:{getDuration()}
      </div>

      {/* Transition Log */}
      <div className="px-4 py-2 border-t border-gray-800">
        <div className="text-gray-500 mb-1">TRANSITION_LOG:</div>
        {transitions.length === 0 ? (
          <div className="text-gray-700">-- no transitions yet --</div>
        ) : (
          transitions.map((t, idx) => (
            <div key={idx}>
              [{t.time}] {t.regime}
            </div>
          ))
        )}
      </div>

      {/* Existing Indicators */}
      <div className="px-4 py-4 space-y-4">
        <RegimeIndicator regime={regime} />
        <FlattenFlagIndicator flatten={flatten} />
        <EntryBlockIndicator block={block} />
      </div>
    </div>
  );
}

export default App;