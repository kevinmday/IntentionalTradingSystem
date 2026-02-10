"""
Causality Invariants — MarketMind Theory Layer

Defines non-negotiable architectural truths about causality
between narrative, quant, theory, and execution.

These invariants exist to PREVENT category errors.

This module is THEORY-ONLY:
- No data access
- No execution logic
- No timing
"""

from enum import Enum
from typing import Final


# -----------------------------
# Causality Domains
# -----------------------------

class SignalDomain(str, Enum):
    """
    Canonical domains of signal authority.
    """

    NARRATIVE = "narrative"
    QUANT = "quant"
    THEORY = "theory"
    EXECUTION = "execution"


# -----------------------------
# Hard Invariants (Doctrine)
# -----------------------------

#: Narrative may authorize participation, but never exits
NARRATIVE_MAY_EXIT: Final[bool] = False

#: Quant may trigger exits, but never authorize entry
QUANT_MAY_AUTHORIZE_ENTRY: Final[bool] = False

#: Quant always retains authority to exit for risk reasons
QUANT_MAY_EXIT: Final[bool] = True

#: Theory defines what should be true, but never acts
THEORY_MAY_EXECUTE: Final[bool] = False

#: Execution may act, but never define theory
EXECUTION_MAY_DEFINE_THEORY: Final[bool] = False


# -----------------------------
# Intent Confirmation Rules
# -----------------------------

#: Intent confirmation must occur BEFORE execution
INTENT_CONFIRMED_BEFORE_EXECUTION: Final[bool] = True

#: Persistence interpretation belongs outside memory
PERSISTENCE_INTERPRETATION_IN_MEMORY: Final[bool] = False


# -----------------------------
# Domain Authority Map
# -----------------------------
# Used by higher layers to assert correct call patterns
# -----------------------------

DOMAIN_AUTHORITY: Final = {
    SignalDomain.NARRATIVE: {
        "authorize_entry": True,
        "trigger_exit": False,
    },
    SignalDomain.QUANT: {
        "authorize_entry": False,
        "trigger_exit": True,
    },
    SignalDomain.THEORY: {
        "authorize_entry": False,
        "trigger_exit": False,
    },
    SignalDomain.EXECUTION: {
        "authorize_entry": False,
        "trigger_exit": False,
    },
}


# -----------------------------
# Assertion Helpers
# -----------------------------

def assert_may_authorize_entry(domain: SignalDomain) -> None:
    """
    Assert that a domain is allowed to authorize entry.
    """
    if not DOMAIN_AUTHORITY[domain]["authorize_entry"]:
        raise AssertionError(
            f"{domain.value} is not allowed to authorize entry"
        )


def assert_may_trigger_exit(domain: SignalDomain) -> None:
    """
    Assert that a domain is allowed to trigger exits.
    """
    if not DOMAIN_AUTHORITY[domain]["trigger_exit"]:
        raise AssertionError(
            f"{domain.value} is not allowed to trigger exit"
        )