class ResearchQuestion:

    def __init__(self, text, horizon_days=30):
        self.text = text
        self.horizon = horizon_days
        self.domain = None

    def classify(self):
        t = self.text.lower()

        if "market" in t:
            self.domain = "markets"

        elif "war" in t or "conflict" in t:
            self.domain = "geopolitics"

        else:
            self.domain = "general"

        return self.domain
