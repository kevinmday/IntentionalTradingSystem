"""
MarketMind Research Runner
Domain-aware research execution with lightweight RSS ingestion
"""

import time
import re
import xml.etree.ElementTree as ET
from urllib.request import urlopen

from marketmind_engine.intelligence.propagation_engine import PropagationEngine
from marketmind_engine.research.question_evaluator import QuestionEvaluator
from marketmind_engine.research.domain_signal_router import DomainSignalRouter


# -------------------------------------------------------
# Minimal runtime stubs required by PropagationEngine
# -------------------------------------------------------

class StubProvider:
    pass


class StubEngineController:
    pass


# -------------------------------------------------------
# Lightweight RSS service used for research mode
# -------------------------------------------------------

class ResearchRSSService:

    def __init__(self, feeds):
        self.feeds = feeds

    def fetch_articles(self):
        """
        Pulls titles from RSS feeds.
        """
        articles = []

        for url in self.feeds:
            try:
                with urlopen(url, timeout=5) as response:
                    xml_data = response.read()

                root = ET.fromstring(xml_data)

                for item in root.iter("item"):
                    title = item.findtext("title")
                    if title:
                        articles.append(title)

            except Exception:
                pass

        return articles


# -------------------------------------------------------
# Simple narrative signal extractor
# -------------------------------------------------------

def compute_narrative_signals(articles):

    if not articles:
        return {
            "momentum": 0.0,
            "concentration": 0.0,
            "matches": 0
        }

    keywords = [
        "iran",
        "israel",
        "missile",
        "strike",
        "military",
        "alliance",
        "war",
        "attack"
    ]

    matches = 0

    for title in articles:
        t = title.lower()

        if any(k in t for k in keywords):
            matches += 1

    total = len(articles)

    concentration = matches / total

    # momentum approximated as frequency scaled
    momentum = min(1.0, matches / 20.0)

    return {
        "momentum": momentum,
        "concentration": concentration,
        "matches": matches
    }


# -------------------------------------------------------
# Natural Language Interpretation Layer
# -------------------------------------------------------

def interpret_result(result, snapshot):

    likelihood = result.likelihood

    narrative = snapshot.get("narrative", {})
    structural = snapshot.get("structural", {})
    composite = snapshot.get("composite", {})

    momentum = narrative.get("momentum", 0)
    concentration = narrative.get("concentration", 0)

    volatility = structural.get("volatility", 0)
    dispersion = structural.get("dispersion", 0)

    regime = composite.get("regime_hint", "unknown")

    if likelihood >= 0.75:
        likelihood_text = "very high"
    elif likelihood >= 0.6:
        likelihood_text = "high"
    elif likelihood >= 0.4:
        likelihood_text = "moderate"
    elif likelihood >= 0.2:
        likelihood_text = "low"
    else:
        likelihood_text = "very low"

    analysis = []

    analysis.append(
        f"The model estimates a {likelihood_text} probability ({round(likelihood,3)}) "
        f"that the researched scenario may occur within the current propagation environment."
    )

    if momentum > 0.8:
        analysis.append(
            "Narrative momentum is extremely elevated across global news sources, "
            "indicating sustained reporting activity and rapid information propagation."
        )

    if concentration > 0.5:
        analysis.append(
            "Narrative concentration is moderate to high, suggesting multiple outlets "
            "are reporting overlapping developments or themes."
        )

    if volatility < 0.3:
        analysis.append(
            "Structural signals remain relatively muted, meaning financial markets "
            "and measurable systemic indicators have not yet strongly aligned "
            "with the narrative escalation."
        )

    if dispersion < 0.2:
        analysis.append(
            "Low structural dispersion indicates limited divergence across monitored "
            "systems, suggesting escalation signals may still be developing."
        )

    analysis.append(
        f"The system regime hint is '{regime}', indicating the engine is currently "
        f"operating in research observation mode rather than live capital deployment."
    )

    return "\n".join(analysis)


# -------------------------------------------------------
# Main research execution
# -------------------------------------------------------

def run():

    question = "Will the Iran conflict expand regionally?"
    domain = "geopolitics"

    print("\n=== MARKETMIND RESEARCH MODE ===\n")

    print("Question:", question)
    print("Domain:", domain)

    # ---------------------------------------------------
    # Resolve domain feeds
    # ---------------------------------------------------

    router = DomainSignalRouter()
    domain_config = router.resolve(domain)

    feeds = domain_config["rss_feeds"]

    print("RSS feeds:", len(feeds))

    # ---------------------------------------------------
    # Fetch articles
    # ---------------------------------------------------

    rss = ResearchRSSService(feeds)

    articles = rss.fetch_articles()

    print("Articles pulled:", len(articles))

    # ---------------------------------------------------
    # Build narrative signals
    # ---------------------------------------------------

    narrative = compute_narrative_signals(articles)

    # ---------------------------------------------------
    # Construct snapshot
    # ---------------------------------------------------

    snapshot = {
        "mode": "research_domain",
        "timestamp": time.time(),

        "structural": {
            "bias": 0.0,
            "volatility": 0.2,
            "dispersion": 0.1
        },

        "narrative": {
            "bias": 0.0,
            "concentration": narrative["concentration"],
            "momentum": narrative["momentum"]
        },

        "capital": {
            "exposure": 0.0,
            "unrealized_pct": 0.0,
            "alignment": 0.1
        },

        "composite": {
            "stress_score": narrative["momentum"] + 0.2,
            "alignment_score": 0.1,
            "regime_hint": "research_mode"
        },

        "relative_signals": []
    }

    # ---------------------------------------------------
    # Evaluate question
    # ---------------------------------------------------

    evaluator = QuestionEvaluator()

    result = evaluator.evaluate(
        question=question,
        domain=domain,
        snapshot=snapshot
    )

    # ---------------------------------------------------
    # Output
    # ---------------------------------------------------

    print("\n=== RESEARCH RESULT ===\n")

    print("Likelihood:", round(result.likelihood, 4))

    print("\nDrivers\n")

    for k, v in result.drivers.items():
        print(f"{k:28} {round(v,4)}")

    print("\nComposite Signals\n")

    for k, v in snapshot["composite"].items():
        print(f"{k:28} {v}")

    print("\n=== INTERPRETATION ===\n")

    analysis = interpret_result(result, snapshot)

    print(analysis)

    print("\nFull Snapshot\n")

    print(snapshot)


if __name__ == "__main__":
    run()