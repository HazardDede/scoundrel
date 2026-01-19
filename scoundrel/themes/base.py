"""
Theming system for the Scoundrel game engine.

Provides a structured way to apply visual or narrative metadata (names, emojis)
to raw card data without altering the underlying gameplay mechanics.
"""

from abc import ABC, abstractmethod
from copy import deepcopy

from pydantic import BaseModel

from scoundrel.models import Deck, Suit, Rank


class Theme(ABC):
    """
    Abstract base class for all deck themes.

    The base class acts as a guard, ensuring that any transformation performed
    by a subclass does not accidentally alter the game balance (card counts
    or type distribution).
    """
    def apply_to(self, deck: Deck) -> Deck:
        """
        Public entry point to apply a theme to a deck.

        Uses deepcopy to preserve the original deck and runs integrity checks
        on the resulting themed deck.

        Args:
            deck (Deck): The deck to apply the theme to.

        Raises:
            RuntimeError: If the theme altered the number of cards or the
                         deck's composition (e.g., turned a monster into a potion).
        """
        themed_deck = self._apply_to(deepcopy(deck))

        if deck.remaining != themed_deck.remaining:
            raise RuntimeError(
                f"Theme is not supposed to change the deck: "
                f"{deck.remaining} vs {themed_deck.remaining} cards"
            )

        if deck.composition != themed_deck.composition:
            raise RuntimeError(
                "Theme is not supposed to change the deck: Composition mismatch"
            )

        return themed_deck

    @abstractmethod
    def _apply_to(self, deck: Deck) -> Deck:
        """
        Internal implementation of the theme transformation logic.

        Subclasses must implement this to return a new or
        modified Deck instance.
        """
        raise NotImplementedError()


class CardIdentity(BaseModel):
    """
    Represents the cosmetic identity of a specific card.

    This is the data used to 'flavor' a raw Rank/Suit combination.
    """
    name: str
    emoji: str


# Mapping of (Suit, Rank) tuples to their thematic Identity.
CardAtlas = dict[tuple[Suit, Rank], CardIdentity]


class AtlasTheme(Theme):
    """
    A theme implementation that uses a dictionary lookup (Atlas)
    to assign names and emojis to cards based on their Suit and Rank.
    """
    def __init__(self, atlas: CardAtlas):
        """
        Initialize the theme with a specific mapping.

        Args:
            atlas: A dictionary where keys are (Suit, Rank) and values
                   are CardIdentity objects.
        """
        self.atlas = atlas

    def _apply_to(self, deck: Deck) -> Deck:
        """
        Iterates through the deck and replaces card instances with
        identities found in the atlas.

        Since card models are frozen, we use model_copy
        to generate updated instances.
        """
        themed_cards = []

        for card in deck.cards:
            identity = self.atlas.get((card.suit, card.rank))
            if not identity:
                # Not found, keep as is
                themed_cards.append(card)
                continue

            # Use model_copy to create a new instance with a modified attribute
            # Remember: We cannot change in-place as the card is frozen
            new_card = card.model_copy(update={
                "name": identity.name,
                "emoji": identity.emoji
            })
            themed_cards.append(new_card)

        return Deck(cards=themed_cards)
