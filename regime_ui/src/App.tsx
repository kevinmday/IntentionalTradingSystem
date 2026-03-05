import React, { useEffect, useState } from "react";
import RegimeIndicator from "./components/RegimeIndicator";
import FlattenFlagIndicator from "./components/FlattenFlagIndicator";
import EntryBlockIndicator from "./components/EntryBlockIndicator";
import PropagationPanel from "./components/PropagationPanel";
import NarrativeRadarPanel from "./components/NarrativeRadarPanel";
import TradeOperationsPanel from "./components/TradeOperationsPanel";
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

  const updated =
    snapshot?.timestamp
      ? new Date(snapshot.timestamp * 1000).toLocaleTimeString()
      : "--:--:--";

  const systemic = regime === "systemic";

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

      return [newEvent, ...prev].slice(0, 20);
    });
  }, [regime, flatten, block]);

  const diagnostics = snapshot?.diagnostics;

  return (
    <div className="w-full min-h-screen text-white font-mono bg-black flex flex-col">

      {/* ================= HEADER ================= */}

      <div className="border-b border-gray-800 px-6 py-3 flex justify-between text-sm tracking-wide">

        <div className="flex gap-6">
          <span className="text-green-400">MARKETMIND OBSERVATORY</span>
          <span>REGIME: {regime.toUpperCase()}</span>
          <span>FLATTEN: {flatten ? "YES" : "NO"}</span>
          <span>BLOCK: {block ? "YES" : "NO"}</span>
        </div>

        <div>
          UPDATED: {updated}
        </div>

      </div>

      {/* ================= MAIN GRID ================= */}

      <div className="flex flex-1">

        {/* LEFT PANEL */}

        <div
          className={`w-1/2 border-r border-gray-800 ${
            systemic ? "bg-red-950" : "bg-black"
          }`}
        >
          <div className="h-full overflow-auto">

            <div className="px-6 py-4 text-xs text-gray-400">
              TIME IN CURRENT STATE: {getDuration()}
            </div>

            <div className="px-6 py-4 space-y-4">
              <RegimeIndicator regime={regime} />
              <FlattenFlagIndicator flatten={flatten} />
              <EntryBlockIndicator block={block} />
            </div>

            <div className="px-6 py-6 border-t border-gray-800 text-xs space-y-4">

              <div className="text-gray-400 tracking-widest">
                DIAGNOSTICS
              </div>

              {diagnostics && (
                <div className="grid grid-cols-2 gap-4">

                  <div>
                    <div>
                      Composite Score: {diagnostics.composite_score?.toFixed?.(3) ?? "--"}
                    </div>

                    <div>
                      Risk Mode: {diagnostics.risk_mode ?? "--"}
                    </div>

                    <div>
                      Flatten All: {diagnostics.flatten_all ? "YES" : "NO"}
                    </div>

                    <div>
                      Block New Entries: {diagnostics.block_new_entries ? "YES" : "NO"}
                    </div>
                  </div>

                  <div>
                    <div>
                      Drawdown Velocity: {diagnostics.macro_inputs?.drawdown_velocity ?? "--"}
                    </div>

                    <div>
                      Liquidity Stress: {diagnostics.macro_inputs?.liquidity_stress ?? "--"}
                    </div>

                    <div>
                      Correlation Spike: {diagnostics.macro_inputs?.correlation_spike ?? "--"}
                    </div>

                    <div>
                      Narrative Shock: {diagnostics.macro_inputs?.narrative_shock ?? "--"}
                    </div>
                  </div>

                </div>
              )}

            </div>

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
        </div>

        {/* RIGHT PANEL */}

        <div className="w-1/2">

          <div className="h-full overflow-auto p-6">
            <PropagationPanel snapshot={snapshot} />
          </div>

        </div>

      </div>

      {/* ================= INTELLIGENCE + TRADE OPS ================= */}

      <div className="border-t border-gray-800 grid grid-cols-2">

        <div className="p-6 border-r border-gray-800">
          <NarrativeRadarPanel />
        </div>

        <div className="p-6">
          <TradeOperationsPanel />
        </div>

      </div>

    </div>
  );
}

export default App;