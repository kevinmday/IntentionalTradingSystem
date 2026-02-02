import time
import uuid
from datetime import datetime, timezone

class EngineClock:
    def __init__(self):
        self._tick = 0
        self._engine_id = uuid.uuid4().hex[:8]

    def now(self) -> dict:
        self._tick += 1
        return {
            "engine_id": self._engine_id,
            "engine_tick": self._tick,
            "engine_time": datetime.now(timezone.utc).isoformat(),
            "monotonic_ns": time.monotonic_ns(),
        }

ENGINE_CLOCK = EngineClock()
