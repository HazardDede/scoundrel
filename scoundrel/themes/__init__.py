"""
Theming subpackage for the Scoundrel engine.

This package provides the infrastructure for applying visual identities
to decks. It includes the base Atlas-based theming logic and
pre-configured themes like the FantasyTheme.
"""

from .base import AtlasTheme, CardAtlas, CardIdentity
from .fantasy import FantasyTheme


__all__ = [
    'AtlasTheme',
    'CardAtlas',
    'CardIdentity',
    'FantasyTheme',
]
