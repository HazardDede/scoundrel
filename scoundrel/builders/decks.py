from abc import ABC, abstractmethod

from scoundrel import models


class DeckBuilder(ABC):
    @abstractmethod
    def build(self, shuffle: bool = True) -> models.Deck:
        """Assembles and returns a new Deck object."""
        raise NotImplementedError()


class StandardDeckBuilder(DeckBuilder):
    def build(self, shuffle: bool = True) -> models.Deck:
        cards = []

        # Create Hearts (Potions 2-10)
        for r in range(2, 11):
            cards.append(models.Potion(suit=models.Suit.HEARTS, rank=r, name=f"Heiltrank"))

        # Create Diamonds (Weapons 2-10)
        for r in range(2, 11):
            cards.append(models.Weapon(suit=models.Suit.DIAMONDS, rank=r, name=f"Schwert"))

        # Create Spades & Clubs (Monsters 2-14)
        for s in [models.Suit.SPADES, models.Suit.CLUBS]:
            for r in range(2, 15):
                cards.append(models.Monster(suit=s, rank=r, name=f"Monster"))

        deck = models.Deck(cards=cards)

        comp = deck.composition
        assert comp.total == 44, f"Standard deck must have 44 cards, but has {comp.total}"

        if shuffle:
            deck.shuffle()

        return deck


class FantasyDeckBuilder(DeckBuilder):
    def __init__(self, easy: bool = False):
        self.easy = bool(easy)

    def build(self, shuffle: bool = True) -> models.Deck:
        cards = [
            models.Monster(suit=models.Suit.CLUBS, rank=2, name="Käfer", emoji="🪲"),
            models.Monster(suit=models.Suit.CLUBS, rank=3, name="Skorpion", emoji="🦂"),
            models.Monster(suit=models.Suit.CLUBS, rank=4, name="Spinne", emoji="🕷️"),
            models.Monster(suit=models.Suit.CLUBS, rank=5, name="Wolf", emoji="🐺"),
            models.Monster(suit=models.Suit.CLUBS, rank=6, name="Bär", emoji="🐻"),
            models.Monster(suit=models.Suit.CLUBS, rank=7, name="Zombie", emoji="🧟"),
            models.Monster(suit=models.Suit.CLUBS, rank=8, name="Geist", emoji="👻"),
            models.Monster(suit=models.Suit.CLUBS, rank=9, name="Skelett", emoji="💀"),
            models.Monster(suit=models.Suit.CLUBS, rank=10, name="Allsehendes Auge", emoji="👁️"),
            models.Monster(suit=models.Suit.CLUBS, rank=11, name="Golem", emoji="🪨"),
            models.Monster(suit=models.Suit.CLUBS, rank=12, name="Vampirlord", emoji="🧛‍"),
            models.Monster(suit=models.Suit.CLUBS, rank=13, name="Dschinn", emoji="🧞"),
            models.Monster(suit=models.Suit.CLUBS, rank=14, name="Drache", emoji="🐉"),

            models.Monster(suit=models.Suit.SPADES, rank=2, name="Fledermaus", emoji="🦇"),
            models.Monster(suit=models.Suit.SPADES, rank=3, name="Schleim", emoji="🟢"),
            models.Monster(suit=models.Suit.SPADES, rank=4, name="Schlange", emoji="🐍"),
            models.Monster(suit=models.Suit.SPADES, rank=5, name="Raubvogel", emoji="🦅"),
            models.Monster(suit=models.Suit.SPADES, rank=6, name="Alligator", emoji="🐊"),
            models.Monster(suit=models.Suit.SPADES, rank=7, name="Pilzkopf", emoji="🍄"),
            models.Monster(suit=models.Suit.SPADES, rank=8, name="Goblin", emoji="👹"),
            models.Monster(suit=models.Suit.SPADES, rank=9, name="Riesenoktopus", emoji="🐙"),
            models.Monster(suit=models.Suit.SPADES, rank=10, name="Gedankenschinder", emoji="🧠"),
            models.Monster(suit=models.Suit.SPADES, rank=11, name="Feuerelementar", emoji="🔥"),
            models.Monster(suit=models.Suit.SPADES, rank=12, name="Frostelementar", emoji="❄️"),
            models.Monster(suit=models.Suit.SPADES, rank=13, name="Chaosgeist", emoji="🧞‍"),
            models.Monster(suit=models.Suit.SPADES, rank=14, name="Blutdämon", emoji="🩸"),
        ]

        for r in range(2, 15 if self.easy else 11):
            cards.append(models.Potion(suit=models.Suit.HEARTS, rank=r, name=f"Heiltrank"))

        for r in range(2, 15 if self.easy else 11):
            cards.append(models.Weapon(suit=models.Suit.DIAMONDS, rank=r, name=f"Schwert"))

        deck = models.Deck(cards=cards)

        if shuffle:
            deck.shuffle()
        return deck


class QuickWinDeckBuilder(DeckBuilder):
    def build(self, shuffle: bool = True) -> models.Deck:
        deck = models.Deck(cards=[
            models.Potion(suit=models.Suit.HEARTS, rank=14, name="Du gewinnst!"),
            models.Potion(suit=models.Suit.HEARTS, rank=13, name="Nimm mich!"),
            models.Monster(suit=models.Suit.SPADES, rank=5, name="???"),
        ])

        if shuffle:
            deck.shuffle()

        return deck


class BeginnerDeckBuilder(DeckBuilder):
    def build(self, shuffle: bool = True) -> models.Deck:
        cards = []

        # Create Hearts (Potions 2-14)
        for r in range(2, 15):
            cards.append(models.Potion(suit=models.Suit.HEARTS, rank=r, name=f"Heiltrank"))

        # Create Diamonds (Weapons 2-12)
        for r in range(2, 13):
            cards.append(models.Weapon(suit=models.Suit.DIAMONDS, rank=r, name=f"Schwert"))

        # Create Spades & Clubs (Monsters 2-14)
        for s in [models.Suit.SPADES, models.Suit.CLUBS]:
            for r in range(2, 15):
                cards.append(models.Monster(suit=s, rank=r, name=f"Monster"))

        deck = models.Deck(cards=cards)

        comp = deck.composition
        assert comp.total == 50, f"Standard deck must have 50 cards, but has {comp.total}"

        if shuffle:
            deck.shuffle()

        return deck
