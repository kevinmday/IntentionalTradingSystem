"""
Ripple Engine

Merges structural domain registry with emergent narrative graph.
Produces layered propagation scores.
"""

from typing import Dict, List, Tuple
from .domain_registry import DOMAIN_REGISTRY
from .narrative_graph import NarrativeGraph


class RippleEngine:

    def __init__(self):
        self.graph = NarrativeGraph()

    # -------------------------------------------------------------
    # Structural Layer
    # -------------------------------------------------------------

    def structural_score(self, domain: str) -> Dict[str, int]:
        """
        Returns weighted structural score by layer depth.
        Layer_0 receives highest weight.
        """

        scores: Dict[str, int] = {}

        if domain not in DOMAIN_REGISTRY:
            return scores

        layers = DOMAIN_REGISTRY[domain]

        for depth, symbols in enumerate(layers.values()):
            weight = max(1, 5 - depth)  # higher weight for closer layers
            for symbol in symbols:
                scores[symbol] = weight

        return scores

    def structural_watchlist(self, domain: str, max_layer: int = 3) -> List[str]:
        """
        Return flattened structural watchlist up to a given layer.
        Excludes layer_0 (primary symbols).
        """

        if domain not in DOMAIN_REGISTRY:
            return []

        layers = DOMAIN_REGISTRY[domain]
        watchlist: List[str] = []

        for depth, (layer_name, symbols) in enumerate(layers.items()):
            if depth == 0:
                continue  # skip primary
            if depth > max_layer:
                break
            watchlist.extend(symbols)

        return watchlist

    def structural_layers(self, domain: str) -> Dict[str, List[str]]:
        """
        Return full structural layer mapping for inspection.
        """
        return DOMAIN_REGISTRY.get(domain, {})

    # -------------------------------------------------------------
    # Emergent + Combined Layer
    # -------------------------------------------------------------

    def combined_score(self, domain: str, items: List) -> Dict[str, float]:
        """
        Combine structural and emergent scores.
        """

        structural = self.structural_score(domain)
        emergent = self.graph.build_symbol_counts(items)

        combined: Dict[str, float] = {}

        for symbol in set(structural.keys()).union(emergent.keys()):
            combined[symbol] = structural.get(symbol, 0) + emergent.get(symbol, 0)

        return dict(sorted(combined.items(), key=lambda x: x[1], reverse=True))

    # -------------------------------------------------------------
    # Domain Utility
    # -------------------------------------------------------------

    def select_top_domain(self, domain_weights: Dict[str, float]) -> str:
        """
        Returns highest-weight domain.
        """

        if not domain_weights:
            return ""

        return max(domain_weights.items(), key=lambda x: x[1])[0]

    # -------------------------------------------------------------
    # Propagation Tier Tagging
    # -------------------------------------------------------------

    def propagation_tiers(
        self, domain: str, items: List
    ) -> List[Tuple[str, float, str]]:
        """
        Returns list of (symbol, score, tier_label)
        """

        combined = self.combined_score(domain, items)
        structural_layers = DOMAIN_REGISTRY.get(domain, {})

        tier_lookup = {}
        for layer_name, symbols in structural_layers.items():
            for s in symbols:
                tier_lookup[s] = layer_name

        results = []

        for symbol, score in combined.items():
            tier = tier_lookup.get(symbol, "emergent")
            results.append((symbol, score, tier))

        return results
