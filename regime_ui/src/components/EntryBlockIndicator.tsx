type Props = {
  blocked: boolean;
};

export default function EntryBlockIndicator({ blocked }: Props) {
  return (
    <div style={{ marginBottom: "1rem" }}>
      <div style={{ fontSize: "0.9rem", opacity: 0.7 }}>New Entries Blocked</div>
      <div
        style={{
          fontSize: "1.25rem",
          fontWeight: "bold",
          color: blocked ? "#ef4444" : "#22c55e",
        }}
      >
        {blocked ? "YES" : "NO"}
      </div>
    </div>
  );
}
