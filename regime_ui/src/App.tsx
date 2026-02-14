import { useRegime } from "./hooks/useRegime";

function App() {
  const { data, error, isOnline } = useRegime(1500);

  return (
    <div style={{ padding: "2rem", fontFamily: "monospace" }}>
      <h1>MarketMind Regime Monitor</h1>

      {!isOnline && <div style={{ color: "red" }}>Backend Offline</div>}
      {error && <div style={{ color: "orange" }}>{error}</div>}

      {data && (
        <pre style={{ marginTop: "1rem" }}>
          {JSON.stringify(data, null, 2)}
        </pre>
      )}
    </div>
  );
}

export default App;
