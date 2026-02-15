class CapitalRecoveryController:
    """
    Deterministic macro capital recovery ramp.

    Independent modifier.
    No engine awareness.
    No domain awareness.
    No symbol awareness.
    """

    RECOVERY_STEPS = 5
    RECOVERY_START_CAP = 0.25

    def __init__(self):
        self._active = False
        self._step = 0

    # --------------------------------------------------
    # Update State
    # --------------------------------------------------

    def update(
        self,
        previous_mode,
        current_mode,
        composite_score,
        stressed_threshold,
    ):
        """
        Update recovery state based on regime transitions.
        """

        # Activate recovery on systemic exit
        if previous_mode in ("systemic", "standby") and current_mode == "normal":
            self._active = True
            self._step = 0
            return

        # Reset if stress reappears
        if composite_score >= stressed_threshold:
            self._active = False
            self._step = 0
            return

        # Advance recovery if active
        if self._active:
            if self._step < self.RECOVERY_STEPS:
                self._step += 1

    # --------------------------------------------------
    # Modifier
    # --------------------------------------------------

    def modifier(self) -> float:
        """
        Returns multiplicative recovery cap.
        Always between 0 and 1.
        """

        if not self._active:
            return 1.0

        progress = self._step / self.RECOVERY_STEPS

        cap = (
            self.RECOVERY_START_CAP
            + progress * (1.0 - self.RECOVERY_START_CAP)
        )

        return max(0.0, min(1.0, cap))