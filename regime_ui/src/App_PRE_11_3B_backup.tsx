import { useRegime } from "./hooks/useRegime";
import RegimeIndicator from "./components/RegimeIndicator";
import FlattenFlagIndicator from "./components/FlattenFlagIndicator";
import EntryBlockIndicator from "./components/EntryBlockIndicator";

function formatTimestamp(ts: number) {
  return new Date(ts * 1000).toLocaleTimeString();
}

function App() {
  const { data, error, isOnline } = useRegime(1500);

  return (
    <div
      style={{
        padding: "2rem",
        fontFamily: "monospace",
        backgroundColor: "#111827",
        minHeight: "100vh",
        color: "#f3f4f6",
      }}
    >
      <h1 style={{ marginBottom: "2rem" }}>
        MarketMind Regime Monitor
      </h1>

      {!isOnline && (
        <div style={{ color: "#ef4444" }}>Backend Offline</div>
      )}

      {error && (
        <div style={{ color: "#f59e0b" }}>{error}</div>
      )}

      {data && (
        <>
          <RegimeIndicator regime={data.regime} />
          <FlattenFlagIndicator flatten={data.flatten_triggered} />
          <EntryBlockIndicator blocked={data.block_new_entries} />

          <div style={{ marginTop: "2rem", opacity: 0.6 }}>
            Last Update: {formatTimestamp(data.timestamp)}
          </div>
        </>
      )}
    </div>
  );
}

export default App;
