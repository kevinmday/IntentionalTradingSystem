class SignalSelector:

    @staticmethod
    def filter_articles(articles, signals):

        selected = []

        for article in articles:
            for s in signals:
                if s in article["text"].lower():
                    selected.append(article)
                    break

        return selected
