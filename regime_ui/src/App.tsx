import React, { useEffect, useState } from "react";
import RegimeIndicator from "./components/RegimeIndicator";
import FlattenFlagIndicator from "./components/FlattenFlagIndicator";
import EntryBlockIndicator from "./components/EntryBlockIndicator";
import { useRegimePolling } from "./hooks/useRegimePolling";

type TransitionEvent = {
  time: string;
  regime: string;
  flatten: boolean;
  block: boolean;
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

  // ---------------------------------------------
  // Phase 11.3B — Duration Counter
  // ---------------------------------------------

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

    return `${hrs}:${mins}:${secs}`;
  };

  // ---------------------------------------------
  // Phase 11.4 — Transition Log
  // ---------------------------------------------

  const [transitionLog, setTransitionLog] = useState<TransitionEvent[]>([]);

  useEffect(() => {
    if (!snapshot) return;

    setTransitionLog((prev) => {
      const last = prev[0];

      if (
        last &&
        last.regime === regime &&
        last.flatten === flatten &&
        last.block === block
      ) {
        return prev;
      }

      const newEvent: TransitionEvent = {
        time: new Date().toLocaleTimeString(),
        regime,
        flatten,
        block,
      };

      return [newEvent, ...prev].slice(0, 20); // cap at 20 entries
    });
  }, [regime, flatten, block]);

  // ---------------------------------------------
  // Diagnostics
  // ---------------------------------------------

  const diagnostics = snapshot?.diagnostics;

  return (
    <div
      className={`min-h-screen text-white font-mono ${
        systemic ? "bg-red-950" : "bg-black"
      }`}
    >
      {/* STATUS STRIP */}
      <div className="border-b border-gray-800 px-4 py-2 text-sm flex justify-between">
        <div className="flex gap-6">
          <span>REGIME: {regime.toUpperCase()}</span>
          <span>FLATTEN: {flatten ? "YES" : "NO"}</span>
          <span>BLOCK: {block ? "YES" : "NO"}</span>
        </div>
        <div>UPDATED: {updated}</div>
      </div>

      {/* DURATION */}
      <div className="px-6 py-4 text-xs text-gray-400">
        TIME IN CURRENT STATE: {getDuration()}
      </div>

      {/* PRIMARY INDICATORS */}
      <div className="px-6 py-4 space-y-4">
        <RegimeIndicator regime={regime} />
        <FlattenFlagIndicator flatten={flatten} />
        <EntryBlockIndicator block={block} />
      </div>

      {/* --------------------------------------------- */}
      {/* DIAGNOSTICS PANEL — ALWAYS VISIBLE */}
      {/* --------------------------------------------- */}

      <div className="px-6 py-6 border-t border-gray-800 text-xs space-y-4">

        <div className="text-gray-400 tracking-widest">
          DIAGNOSTICS
        </div>

        {diagnostics && (
          <div className="grid grid-cols-2 gap-4">

            <div>
              <div>Composite Score: {diagnostics.composite_score?.toFixed(3)}</div>
              <div>Risk Mode: {diagnostics.risk_mode}</div>
              <div>Stressed Threshold: {diagnostics.stressed_threshold}</div>
              <div>Flatten All: {diagnostics.flatten_all ? "YES" : "NO"}</div>
              <div>Block New Entries: {diagnostics.block_new_entries ? "YES" : "NO"}</div>
            </div>

            <div>
              <div>Drawdown Velocity: {diagnostics.macro_inputs?.drawdown_velocity}</div>
              <div>Liquidity Stress: {diagnostics.macro_inputs?.liquidity_stress}</div>
              <div>Correlation Spike: {diagnostics.macro_inputs?.correlation_spike}</div>
              <div>Narrative Shock: {diagnostics.macro_inputs?.narrative_shock}</div>
              <div>Structural Confirmation: {diagnostics.macro_inputs?.structural_confirmation}</div>
            </div>

          </div>
        )}

      </div>

      {/* --------------------------------------------- */}
      {/* TRANSITION LOG */}
      {/* --------------------------------------------- */}

      <div className="px-6 py-6 border-t border-gray-800 text-xs space-y-2">

        <div className="text-gray-400 tracking-widest">
          TRANSITION LOG
        </div>

        <div className="space-y-1">
          {transitionLog.map((entry, index) => (
            <div key={index} className="flex justify-between text-gray-300">
              <span>{entry.time}</span>
              <span>{entry.regime.toUpperCase()}</span>
              <span>F:{entry.flatten ? "1" : "0"}</span>
              <span>B:{entry.block ? "1" : "0"}</span>
            </div>
          ))}
        </div>

      </div>
    </div>
  );
}

export default App;