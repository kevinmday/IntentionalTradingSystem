"""
Static domain → asset adjacency tables (Phase-4E).

Deterministic mappings that encode known structural exposure
between intention domains and assets.
"""

from typing import Dict, List, Tuple


# strength ∈ [0.0, 1.0] expresses coupling, not probability
DOMAIN_ASSET_MAP: Dict[str, List[Tuple[str, float]]] = {

    # --- Defense / National Security ---
    "Defense AI": [
        ("PLTR", 0.85),
        ("LMT", 0.80),
        ("NOC", 0.75),
        ("RTX", 0.70),
        ("BA",  0.60),
    ],

    # --- Energy Security ---
    "Energy Security": [
        ("XOM", 0.80),
        ("CVX", 0.78),
        ("SLB", 0.72),
        ("OXY", 0.65),
    ],

    # --- AI Infrastructure ---
    "AI Infrastructure": [
        ("NVDA", 0.90),
        ("AMD",  0.82),
        ("MSFT", 0.75),
        ("GOOGL",0.70),
    ],

    # --- Healthcare / Biotech ---
    "Biotech Regulation": [
        ("MRNA", 0.75),
        ("BNTX", 0.70),
        ("REGN", 0.68),
        ("VRTX", 0.65),
    ],
}