"""
Configuration flavors for deck generation.

This module defines the available deck presets, which determine the
size and difficulty of the generated Scoundrel deck.
"""

from enum import Enum


class DeckFlavor(str, Enum):
    """
    Defines the size and composition presets for a new deck.

    Attributes:
        Beginner: High potion count and moderate monsters for learning the game.
        Quick: A smaller deck for faster sessions with adjusted monster ranks.
        Standard: The classic Scoundrel experience with a full 44-card distribution.
    """
    BEGINNER = "beginner"
    QUICK = "quick"
    STANDARD = "standard"
