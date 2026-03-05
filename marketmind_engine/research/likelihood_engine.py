class LikelihoodEngine:

    def __init__(self):
        self.fils = 0
        self.ucip = 0
        self.ttcf = 0

    def compute(self, articles):

        mentions = len(articles)
        publishers = set(a["publisher"] for a in articles)

        self.fils = min(1.0, mentions * 0.05)
        self.ucip = min(1.0, len(publishers) * 0.1)
        self.ttcf = 0

        likelihood = (self.fils + self.ucip) / 2

        return likelihood
