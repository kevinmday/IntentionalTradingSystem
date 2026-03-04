from marketmind_engine.config.feed_loader import load_feeds_by_type


class FeedRegistry:
    """
    Provides RSS feed URLs sourced from YAML configuration.
    No domain or weight logic exposed here.
    """

    def __init__(self):
        feeds = load_feeds_by_type("rss")
        self.feeds = [f.url for f in feeds]

    def get_feeds(self):
        return self.feeds
