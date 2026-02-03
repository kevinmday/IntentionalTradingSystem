from datetime import datetime, timezone
import time
import uuid


class EngineClock:
    def __init__(self):
        self.engine_id = uuid.uuid4().hex[:8]
        self._tick = 0
        self._frozen = False
        self._frozen_time = None
        self._frozen_monotonic = None

    # -------------------------
    # Core time
    # -------------------------

    def now(self) -> dict:
        """
        Authoritative engine time.
        """
        if self._frozen:
            return {
                "engine_id": self.engine_id,
                "engine_tick": self._tick,
                "engine_time": self._frozen_time.isoformat(),
                "monotonic_ns": self._frozen_monotonic,
                "frozen": True,
            }

        self._tick += 1
        now = datetime.now(timezone.utc)
        mono = time.monotonic_ns()

        return {
            "engine_id": self.engine_id,
            "engine_tick": self._tick,
            "engine_time": now.isoformat(),
            "monotonic_ns": mono,
            "frozen": False,
        }

    # -------------------------
    # Freeze controls
    # -------------------------

    def freeze(self, at_time: datetime | None = None):
        """
        Freeze engine time.
        """
        self._frozen = True
        self._frozen_time = at_time or datetime.now(timezone.utc)
        self._frozen_monotonic = time.monotonic_ns()

    def unfreeze(self):
        """
        Resume live time.
        """
        self._frozen = False
        self._frozen_time = None
        self._frozen_monotonic = None

    def is_frozen(self) -> bool:
        return self._frozen


# ==================================================
# SINGLE AUTHORITATIVE ENGINE CLOCK INSTANCE
# ==================================================

ENGINE_CLOCK = EngineClock()
