class TracebackReport:

    @staticmethod
    def generate(engine, articles):

        return {
            "FILS": engine.fils,
            "UCIP": engine.ucip,
            "TTCF": engine.ttcf,
            "article_count": len(articles)
        }
