export interface RegimeSnapshot {
  regime: string;
  block_new_entries: boolean;
  flatten_triggered: boolean;
  timestamp: number;
}

export async function fetchRegime(): Promise<RegimeSnapshot> {
  const response = await fetch("http://localhost:5001/regime");

  if (!response.ok) {
    throw new Error("Failed to fetch regime");
  }

  return response.json();
}
