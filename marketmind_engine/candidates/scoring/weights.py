# marketmind_engine/candidates/scoring/weights.py

"""
PHASE-6B SCORING WEIGHTS

This module defines scoring weights ONLY.
It contains no logic, no conditionals, and no side effects.

These values are policy inputs, not behavior.
They may be tuned later without modifying scoring mechanics.
"""

# Canonical component weights
COMPONENT_WEIGHTS = {
    "intention_strength": 1.0,
    "coherence": 1.0,
    "chaos_discount": 1.0,
    "domain_weight": 1.0,
}

# Priority band thresholds (NOT APPLIED YET)
PRIORITY_THRESHOLDS = {
    "HOT": 0.75,
    "WARM": 0.40,
    "BACKLOG": 0.00,
}