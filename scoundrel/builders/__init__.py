"""
Deck building and configuration tools.

This package provides the infrastructure for creating game decks with
different compositions and difficulty presets (flavors).
"""

from .decks import DeckBuilder, StandardDeckBuilder
from .flavor import DeckFlavor

__all__ = [
    'DeckBuilder',
    'DeckFlavor',
    'StandardDeckBuilder',
]
