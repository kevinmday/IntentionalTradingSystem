class MockNarrativeAdapter:
    """
    Deterministic narrative shock injector.
    Used for replay-safe testing.
    """

    def __init__(self, shock_value: float):
        self._shock_value = shock_value

    def compute_narrative_shock(self) -> float:
        return self._shock_value