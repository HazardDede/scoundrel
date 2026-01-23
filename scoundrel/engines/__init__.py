"""
Logic engines for the Scoundrel game.

This package contains the core rule implementations. The RulesEngine
governs the interaction between game entities and enforces the
mechanics of the Scoundrel card game.
"""

from .rules import StandardRulesEngine, RulesEngine

__all__ = [
    'StandardRulesEngine',
    'RulesEngine'
]
