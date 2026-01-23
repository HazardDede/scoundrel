"""
Deck generation logic for Scoundrel.

This module provides the machinery to create card decks based on different
gameplay flavors. It uses the Builder pattern to separate the assembly
process from the specific card distributions.
"""

from abc import ABC, abstractmethod

from scoundrel import models

from .flavor import DeckFlavor


class DeckBuilder(ABC):
    """
    Abstract base class for deck construction.

    Provides a template method 'build' that handles common deck setup
    steps like shuffling, while delegating the specific card creation
    to subclasses.
    """

    @classmethod
    @abstractmethod
    def supported_flavors(cls) -> list[str]:
        """
        Returns a list of supported flavors (like variants of the deck, e.g. easy / hard).
        Each DeckBuilder should allow to pass a flavor argument when instantiating.
        """

    @classmethod
    @abstractmethod
    def default_flavor(cls) -> str:
        """Returns the default flavor of the deck."""

    @property
    @abstractmethod
    def flavor(self) -> str:
        """Returns the current flavor of the deck."""

    def build(self, shuffle: bool = True) -> models.Deck:
        """
        The main entry point to create a ready-to-play deck.

        Args:
            shuffle: If True, the deck will be randomized before being returned.

        Returns:
            A populated models.Deck instance.
        """
        deck = self._build()

        if shuffle:
            deck.shuffle()
        return deck

    @abstractmethod
    def _build(self) -> models.Deck:
        """
        Internal implementation of card creation.
        """
        raise NotImplementedError()


class StandardDeckBuilder(DeckBuilder):
    """
    The default builder for Scoundrel decks.

    Creates cards (Potions, Weapons, Monsters) based on pre-defined
    max-rank configurations for different gameplay flavors.
    """

    # Mapping of Flavor to max ranks: (potions, weapons, monsters)
    # Note that cards always start at rank 2.
    _CONFIG_MAX_RANKS = {
        DeckFlavor.BEGINNER: (14, 14, 14),
        DeckFlavor.QUICK: (5, 5, 8),
        DeckFlavor.STANDARD: (10, 10, 14)
    }

    def __init__(self, flavor: str | DeckFlavor = DeckFlavor.STANDARD):
        """
        Initializes the builder with a specific flavor.

        Args:
            flavor: The preset that determines the deck's composition.
        """
        if flavor not in self._CONFIG_MAX_RANKS:
            raise ValueError(
                f"The flavor '{flavor.value if isinstance(flavor, DeckFlavor) else str(flavor)}' is not supported."
            )

        self._flavor = flavor if isinstance(flavor, DeckFlavor) else DeckFlavor(flavor)

    @classmethod
    def supported_flavors(cls) -> list[str]:
        return [
            flavor.value for flavor in cls._CONFIG_MAX_RANKS
        ]

    @classmethod
    def default_flavor(cls) -> str:
        return DeckFlavor.STANDARD.value

    @property
    def flavor(self) -> str:
        return self._flavor.value

    def _build(self) -> models.Deck:
        """
        Assembles the card list based on the chosen flavor's rank limits.

        Uses hardcoded default names ('Heiltrank', etc.)
        which are intended to be replaced later by a Theme.
        """
        cards: list[models.AnyCard] = []

        r_potion, r_weapon, r_monster = self._CONFIG_MAX_RANKS[self._flavor]

        for r in range(2, r_potion + 1):
            cards.append(models.Potion(suit=models.Suit.HEARTS, rank=r, name="Heiltrank"))

        for r in range(2, r_weapon + 1):
            cards.append(models.Weapon(suit=models.Suit.DIAMONDS, rank=r, name="Schwert"))

        for s in [models.Suit.SPADES, models.Suit.CLUBS]:
            for r in range(2, r_monster + 1):
                cards.append(models.Monster(suit=s, rank=r, name="Monster"))

        deck = models.Deck(cards=cards)

        comp = deck.composition
        total_cards = r_potion + r_weapon + r_monster * 2 - 4
        assert comp.total == total_cards, f"This deck must have {total_cards} cards, but has {comp.total}"

        return deck
