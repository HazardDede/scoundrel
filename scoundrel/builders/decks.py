from abc import ABC, abstractmethod

from scoundrel import models

from .flavor import DeckFlavor


class DeckBuilder(ABC):
    def build(self, shuffle: bool = True) -> models.Deck:
        """Assembles and returns a new Deck object."""
        deck = self._build()

        if shuffle:
            deck.shuffle()
        return deck

    @abstractmethod
    def _build(self) -> models.Deck:
        raise NotImplementedError()


class StandardDeckBuilder(DeckBuilder):
    _CONFIG_MAX_RANKS = {  # Flavor -> (potion, weapon, monster)
        DeckFlavor.Beginner: (14, 14, 14),
        DeckFlavor.Quick: (5, 5, 8),
        DeckFlavor.Standard: (10, 10, 14)
    }

    def __init__(self, flavor: DeckFlavor = DeckFlavor.Standard):
        self.flavor = flavor

    def _build(self) -> models.Deck:
        cards = []

        r_potion, r_weapon, r_monster = self._CONFIG_MAX_RANKS[self.flavor]

        for r in range(2, r_potion + 1):
            cards.append(models.Potion(suit=models.Suit.HEARTS, rank=r, name=f"Heiltrank"))

        for r in range(2, r_weapon + 1):
            cards.append(models.Weapon(suit=models.Suit.DIAMONDS, rank=r, name=f"Schwert"))

        for s in [models.Suit.SPADES, models.Suit.CLUBS]:
            for r in range(2, r_monster + 1):
                cards.append(models.Monster(suit=s, rank=r, name=f"Monster"))

        deck = models.Deck(cards=cards)

        comp = deck.composition
        total_cards = r_potion + r_weapon + r_monster * 2 - 4
        assert comp.total == total_cards, f"This deck must have {total_cards} cards, but has {comp.total}"

        return deck
