# marketmind/trade_logic.py

from datetime import datetime
import hashlib

def generate_trade_cards(parsed_articles):
    """
    Generate trade card data from parsed article list.
    Each article becomes a trade candidate with a hashed ID.

    :param parsed_articles: List of article dictionaries from parse_default_rss
    :return: List of trade card dictionaries
    """
    trade_cards = []

    for article in parsed_articles:
        trade_id = hashlib.md5(article['link'].encode()).hexdigest()[:8]
        trade_card = {
            "id": trade_id,
            "title": article.get("title", "No Title"),
            "link": article.get("link", ""),
            "summary": article.get("summary", ""),
            "published": article.get("published", "Unknown"),
            "timestamp": datetime.now().isoformat(),
            "status": "PENDING",
            "priority": "NORMAL"
        }
        trade_cards.append(trade_card)

    return trade_cards


def queue_trades(trade_cards):
    """
    Queues trade cards into memory or logging system.
    Currently just prints queued items for debugging.

    :param trade_cards: List of trade card dictionaries
    :return: None
    """
    print(f"[QUEUE] Queuing {len(trade_cards)} trade(s)...")

    for card in trade_cards:
        print(f"[TRADE QUEUED] {card['id']} - {card['title']}")

    # In production: write to DB or append to queueing service

def discover_trades(metrics, ripple_domain):
    # Basic stub — replace with real filtering logic later
    # This could be tied to sector, ripple_domain, or sentiment filtering
    if ripple_domain == "social":
        return ["META", "SNAP"]
    elif ripple_domain == "geopolitical":
        return ["LMT", "RTX"]
    else:
        return ["SPY", "AAPL"]
