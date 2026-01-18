from abc import ABC, abstractmethod
from pydantic import BaseModel


from scoundrel import models


class BaseDeckBuilder(ABC):
    @abstractmethod
    def build_deck(self, shuffle: bool = True) -> models.Deck:
        """Assembles and returns a new Deck object."""
        raise NotImplementedError()


class StandardBuilder(BaseDeckBuilder):
    def build_deck(self, shuffle: bool = True) -> models.Deck:
        cards = []
        
        # Create Hearts (Potions 2-10)
        for r in range(2, 11):
            cards.append(models.Potion(suit=models.Suit.HEARTS, rank=r, name=f"Health Potion {r}"))
        
        # Create Diamonds (Weapons 2-10)
        for r in range(2, 11):
            cards.append(models.Weapon(suit=models.Suit.DIAMONDS, rank=r, name=f"Shield/Sword {r}"))
            
        # Create Spades & Clubs (Monsters 2-14)
        for s in [models.Suit.SPADES, models.Suit.CLUBS]:
            for r in range(2, 15):
                cards.append(models.Monster(suit=s, rank=r, name=f"Dungeon Monster {r}"))

        deck = models.Deck(cards=cards)

        comp = deck.composition
        assert comp.total == 44, f"Standard deck must have 44 cards, but has {comp.total}"

        if shuffle:
            deck.shuffle()
        
        return deck


class BeginnerDeckBuilder(BaseDeckBuilder):
    def build_deck(self, shuffle: bool = True) -> models.Deck:
        cards = []
        
        # Create Hearts (Potions 2-14)
        for r in range(2, 15):
            cards.append(models.Potion(suit=models.Suit.HEARTS, rank=r, name=f"Health Potion {r}"))
        
        # Create Diamonds (Weapons 2-12)
        for r in range(2, 13):
            cards.append(models.Weapon(suit=models.Suit.DIAMONDS, rank=r, name=f"Shield/Sword {r}"))
            
        # Create Spades & Clubs (Monsters 2-14)
        for s in [models.Suit.SPADES, models.Suit.CLUBS]:
            for r in range(2, 15):
                cards.append(models.Monster(suit=s, rank=r, name=f"Dungeon Monster {r}"))

        deck = models.Deck(cards=cards)

        comp = deck.composition
        assert comp.total == 50, f"Standard deck must have 50 cards, but has {comp.total}"

        if shuffle:
            deck.shuffle()
        
        return deck

