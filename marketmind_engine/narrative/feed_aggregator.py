from dataclasses import dataclass
from typing import List, Dict
from marketmind_engine.config.feed_loader import load_feeds_by_type


@dataclass(frozen=True)
class NarrativeItem:
    title: str
    link: str
    source: str
    domain: str
    weight: float


class FeedAggregator:
    """
    Normalizes raw RSS entries and attaches metadata.
    No engine logic. No trading logic.
    """

    def __init__(self):
        self.feed_configs = {
            f.url: f for f in load_feeds_by_type("rss")
        }

    def aggregate(self, raw_entries: Dict[str, List[dict]]) -> List[NarrativeItem]:
        """
        raw_entries:
            {
                "feed_url": [ {entry_dict}, {entry_dict} ]
            }
        """

        seen_links = set()
        results: List[NarrativeItem] = []

        for feed_url, entries in raw_entries.items():
            config = self.feed_configs.get(feed_url)

            if not config:
                continue

            for entry in entries:
                link = entry.get("link")
                title = entry.get("title", "")
                source = feed_url

                if not link or link in seen_links:
                    continue

                seen_links.add(link)

                results.append(
                    NarrativeItem(
                        title=title,
                        link=link,
                        source=source,
                        domain=config.domain,
                        weight=config.weight,
                    )
                )

        return results