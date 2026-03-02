import re
from collections import defaultdict
from marketmind_engine.narrative.rss.feed_registry import FeedRegistry
from marketmind_engine.narrative.rss.rss_fetcher import RSSFetcher
from marketmind_engine.narrative.rss.narrative_buffer import NarrativeBuffer
from marketmind_engine.narrative.rss.rss_worker import RSSWorker

print("=== RSS EXTENDED DISCOVERY PROBE ===")

registry = FeedRegistry()
fetcher = RSSFetcher()
buffer = NarrativeBuffer()
worker = RSSWorker(registry, fetcher, buffer)

print("Polling feeds once...")
worker.poll_once()

items = buffer.snapshot()

print(f"\nTotal normalized items: {len(items)}\n")

# --- DOMAIN CLUSTERING ---
domain_weight = defaultdict(float)
for item in items:
    domain_weight[item.domain] += item.weight

ranked_domains = sorted(domain_weight.items(), key=lambda x: x[1], reverse=True)

print("=== HOT DOMAINS ===")
for d, w in ranked_domains:
    print(f"{d} | weight={round(w,2)}")

print()

# --- SYMBOL EXTRACTION ---
ticker_pattern = re.compile(r"\b[A-Z]{2,5}\b")
symbol_counts = defaultdict(int)
symbol_domains = defaultdict(set)

for item in items:
    tokens = ticker_pattern.findall(item.title)
    for token in tokens:
        # crude filter to remove common words
        if token not in ["AI", "IPO", "FDA", "USA", "US"]:
            symbol_counts[token] += 1
            symbol_domains[token].add(item.domain)

ranked_symbols = sorted(symbol_counts.items(), key=lambda x: x[1], reverse=True)

print("=== CANDIDATE SYMBOLS ===\n")

for sym, count in ranked_symbols[:15]:
    print(f"{sym} | mentions={count} | domains={list(symbol_domains[sym])}")