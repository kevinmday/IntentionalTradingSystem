type Props = {
  regime: string;
};

function getColor(regime: string) {
  switch (regime.toLowerCase()) {
    case "normal":
      return "#22c55e"; // green
    case "stressed":
      return "#f59e0b"; // amber
    case "systemic":
      return "#ef4444"; // red
    default:
      return "#6b7280"; // gray
  }
}

export default function RegimeIndicator({ regime }: Props) {
  return (
    <div style={{ marginBottom: "1rem" }}>
      <div style={{ fontSize: "0.9rem", opacity: 0.7 }}>Regime</div>
      <div
        style={{
          fontSize: "1.5rem",
          fontWeight: "bold",
          color: getColor(regime),
        }}
      >
        {regime.toUpperCase()}
      </div>
    </div>
  );
}
