class DeterministicIgnitionSurface:
    """
    Deterministic latency simulation surface.

    Scenario:
    - Ignition at t=0
    - Weak coupling before t=200
    - Strong coupling from t=200 onward
    """

    def __init__(self):
        self.ignition_time = 0

    def __call__(self, clock):
        now = clock.now()

        if now < 200:
            return {
                "ignition_time": self.ignition_time,
                "price_delta": 0.005,   # below threshold
                "volume_ratio": 1.0,    # below threshold
            }

        return {
            "ignition_time": self.ignition_time,
            "price_delta": 0.02,      # above threshold
            "volume_ratio": 1.5,      # above threshold
        }