"""
MarketMind Domain Signal Router

Maps research domains to signal sources.
Provides RSS feeds and signal categories used by the research engine.
"""

from typing import Dict, Any


class DomainSignalRouter:

    def resolve(self, domain: str) -> Dict[str, Any]:

        domain = domain.lower()

        # ---------------------------------------------------------
        # GEOPOLITICS
        # ---------------------------------------------------------

        if domain == "geopolitics":
            return {
                "signals": [
                    "military",
                    "diplomatic",
                    "alliance",
                    "energy",
                    "defense",
                    "conflict",
                    "sanctions",
                ],
                "rss_feeds": [

                    # global wire services
                    "https://feeds.reuters.com/Reuters/worldNews",
                    "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
                    "https://feeds.bbci.co.uk/news/world/rss.xml",

                    # international reporting
                    "https://www.aljazeera.com/xml/rss/all.xml",
                    "https://www.theguardian.com/world/rss",
                    "https://www.ft.com/world?format=rss",

                    # defense / security
                    "https://www.defensenews.com/arc/outboundfeeds/rss/",

                    # regional conflict reporting
                    "https://www.jpost.com/rss/rssfeedsfrontpage.aspx",
                    "https://www.arabnews.com/rss.xml",
                ],
            }

        # ---------------------------------------------------------
        # MACRO ECONOMICS
        # ---------------------------------------------------------

        if domain == "macro":
            return {
                "signals": [
                    "inflation",
                    "rates",
                    "central_bank",
                    "liquidity",
                    "recession",
                    "credit",
                ],
                "rss_feeds": [
                    "https://feeds.reuters.com/reuters/businessNews",
                    "https://rss.nytimes.com/services/xml/rss/nyt/Economy.xml",
                    "https://www.ft.com/?format=rss",
                    "https://www.marketwatch.com/rss/topstories",
                ],
            }

        # ---------------------------------------------------------
        # TECHNOLOGY
        # ---------------------------------------------------------

        if domain == "technology":
            return {
                "signals": [
                    "ai",
                    "semiconductors",
                    "cloud",
                    "cybersecurity",
                    "chips",
                    "automation",
                ],
                "rss_feeds": [
                    "https://feeds.arstechnica.com/arstechnica/index",
                    "https://www.theverge.com/rss/index.xml",
                    "https://techcrunch.com/feed/",
                    "https://www.wired.com/feed/rss",
                ],
            }

        # ---------------------------------------------------------
        # DEFAULT FALLBACK
        # ---------------------------------------------------------

        return {
            "signals": [],
            "rss_feeds": [],
        }