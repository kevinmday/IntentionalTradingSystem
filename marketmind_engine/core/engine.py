"""
MarketMind Engine
Engine-first architecture.
"""

from __future__ import annotations


class Engine:
    """
    Core orchestration engine for MarketMind.
    This is intentionally minimal at first.
    """

    def __init__(self, context=None):
        self.context = context

    def run(self):
        """
        Placeholder run loop.
        """
        raise NotImplementedError("Engine.run() not implemented yet")

