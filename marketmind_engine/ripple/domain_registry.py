"""
Structured Ripple Registry

Defines deterministic ripple trees per domain.
No runtime logic. Pure data.
"""

from typing import Dict, List


DOMAIN_REGISTRY: Dict[str, Dict[str, List[str]]] = {

    "defense": {
        "layer_0": ["LMT", "RTX"],
        "layer_1": ["NOC", "GD", "HII", "LHX", "BA"],
        "layer_2": ["ITA", "XAR", "PPA"],
        "layer_3": ["KTOS", "AVAV", "MRCY", "AIR", "CW"],
        "layer_4": []  # reserved for micro-cap expansion
    },

    "ai-bio": {
        "layer_0": ["RXRX"],
        "layer_1": ["TEM", "CRSP", "DNA"],
        "layer_2": ["XBI", "ARKG"],
        "layer_3": [],
        "layer_4": []
    }

}