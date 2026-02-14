type Props = {
  flatten: boolean;
};

export default function FlattenFlagIndicator({ flatten }: Props) {
  return (
    <div style={{ marginBottom: "1rem" }}>
      <div style={{ fontSize: "0.9rem", opacity: 0.7 }}>Flatten Triggered</div>
      <div
        style={{
          fontSize: "1.25rem",
          fontWeight: "bold",
          color: flatten ? "#ef4444" : "#22c55e",
        }}
      >
        {flatten ? "YES" : "NO"}
      </div>
    </div>
  );
}
