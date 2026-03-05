import React, { useEffect, useState } from "react";

type DomainPressure = {
  domain: string;
  score: number;
};

type SymbolSignal = {
  symbol: string;
  mentions: number;
  momentum: number;
};

type RadarSnapshot = {
  domains: DomainPressure[];
  symbols: SymbolSignal[];
  updated: string;
};

export default function NarrativeRadarPanel() {

  const [snapshot, setSnapshot] = useState<RadarSnapshot | null>(null);

  const fetchRadar = async () => {
    try {
      const res = await fetch("/api/narrative_radar");
      const data = await res.json();
      setSnapshot(data);
    } catch {
      // silent fail for now
    }
  };

  useEffect(() => {

    fetchRadar();

    const interval = setInterval(() => {
      fetchRadar();
    }, 5000);

    return () => clearInterval(interval);

  }, []);

  return (

    <div className="space-y-4">

      <div className="text-gray-400 tracking-widest text-xs">
        NARRATIVE RADAR
      </div>

      {!snapshot && (
        <div className="text-gray-500 text-xs">
          awaiting radar feed...
        </div>
      )}

      {snapshot && (
        <>

          {/* DOMAIN PRESSURE */}

          <div className="text-xs">

            <div className="text-gray-400 mb-2">
              DOMAIN PRESSURE
            </div>

            <div className="space-y-1">

              {snapshot.domains.map((d) => (

                <div
                  key={d.domain}
                  className="flex justify-between text-gray-300"
                >
                  <span>{d.domain}</span>

                  <span>
                    {Math.round(d.score)}
                  </span>

                </div>

              ))}

            </div>

          </div>

          {/* SYMBOL EMERGENCE */}

          <div className="text-xs mt-4">

            <div className="text-gray-400 mb-2">
              EMERGING SYMBOLS
            </div>

            <div className="space-y-1">

              {snapshot.symbols.map((s) => (

                <div
                  key={s.symbol}
                  className="flex justify-between text-gray-300"
                >

                  <span>{s.symbol}</span>

                  <span>
                    mentions:{s.mentions}
                  </span>

                  <span>
                    momentum:{s.momentum.toFixed(2)}
                  </span>

                </div>

              ))}

            </div>

          </div>

        </>
      )}

    </div>

  );
}