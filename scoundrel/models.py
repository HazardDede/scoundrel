from enum import Enum
from typing import Literal, Optional, Annotated, Union

import random

from pydantic import BaseModel, Field, computed_field, ConfigDict

from scoundrel import exc


CONST_MONSTER = "monster"
CONST_POTION = "potion"
CONST_WEAPON = "weapon"

class Suit(str, Enum):
    SPADES = "Spades"     # Pik (Monster)
    CLUBS = "Clubs"       # Kreuz (Monster)
    DIAMONDS = "Diamonds" # Karo (Waffen)
    HEARTS = "Hearts"     # Herz (Heiltränke)


class ActionPreview(BaseModel):
    """Provides information about the consequences of an action."""
    damage_taken: int = 0
    healing_received: int = 0
    is_lethal: bool = False  # Would this action kill the player?


class Card(BaseModel):
    # This makes the card immutable and hashable
    model_config = ConfigDict(frozen=True)

    suit: Suit
    rank: int  # 2-10, 11 (J), 12 (Q), 13 (K), 14 (A)
    name: str
    type: str  # Override in child classes

    @computed_field
    @property
    def card_id(self) -> str:
        # Deterministic ID based on suit and rank (e.g., "SPADES_14")
        return f"{self.suit.value.upper()}_{self.rank}"

    def __str__(self) -> str:
        """User-friendly string representation."""
        return f"{self.name} ({self.card_id})"

    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return f"Card(id={self.card_id}, type={self.type})"


class Monster(Card):
    type: Literal["monster"] = CONST_MONSTER

    @property
    def strength(self) -> int:
        # Base strength is tied to rank, but easily modifiable later
        return self.rank


class Potion(Card):
    type: Literal["potion"] = CONST_POTION
    
    @property
    def potency(self) -> int:
        return self.rank


class Weapon(Card):
    type: Literal["weapon"] = CONST_WEAPON
    
    @property
    def protection(self) -> int:
        return self.rank


AnyCard = Annotated[Union[Monster, Potion, Weapon], Field(discriminator='type')]


class EquippedWeapon(BaseModel):
    weapon: Weapon
    slain_monsters: list[Monster] = Field(default_factory=list)

    @computed_field
    @property
    def last_slain_monster(self) -> Optional[Monster]:
        """Gibt das zuletzt besiegte Monster zurück, falls vorhanden."""
        return self.slain_monsters[-1] if self.slain_monsters else None


class Player(BaseModel):
    max_life: int = 20
    current_life: int = 20

    weapon: Optional[EquippedWeapon] = None

    @property
    def is_dead(self) -> bool:
        return self.current_life <= 0

    @property
    def has_weapon(self) -> bool:
        return self.weapon is not None

    def heal(self, amount: int) -> None:
        if amount < 0: 
            raise ValueError("Positive value expected")
        self.current_life = min(self.max_life, self.current_life + amount)

    def take_damage(self, amount: int) -> None:
        if amount < 0: 
            raise ValueError("Positive value expected")
        self.current_life = max(0, self.current_life - amount)


class Room(BaseModel):
    cards: list[AnyCard] = Field(default_factory=list)
    potions_used: int = Field(0, ge=0)

    @property
    def remaining(self) -> int:
        return len(self.cards)

    def exists(self, card: AnyCard) -> bool:
        return card.card_id in [c.card_id for c in self.cards]

    def interacted(self, card: AnyCard) -> None:
        """
        Removes a card from the room based on its deterministic ID.
        """
        # Find index and card at once
        try:
            idx, target_card = next(
                ((i, c) for i, c in enumerate(self.cards) if c.card_id == card.card_id)
            )
            self.cards.pop(idx)
        except StopIteration:
            raise ValueError(f"Card {card.card_id} not found in current room.")


class DeckComposition(BaseModel):
    """
    Represents the exact count of card types within a deck.
    """
    monsters: int
    potions: int
    weapons: int

    @property
    def total(self) -> int:
        return self.monsters + self.potions + self.weapons


class Deck(BaseModel):
    cards: list[AnyCard] = Field(default_factory=list)
    bottomed_cards: int = 0

    def shuffle(self) -> None:
        random.shuffle(self.cards)

    def draw(self) -> AnyCard:
        if len(self.cards) < 1:
            raise exc.DeckEmptyError("Deck is empty")  # TODO: Specific Exception
        
        return self.cards.pop()

    @computed_field
    @property
    def remaining(self) -> int:
        return len(self.cards)

    @computed_field
    @property
    def is_empty(self) -> bool:
        return len(self.cards) == 0

    @property
    def composition(self) -> DeckComposition:
        """
        Analyzes the current state of the deck and returns the counts of each card type.
        """
        monsters = sum(1 for c in self.cards if isinstance(c, Monster))
        potions = sum(1 for c in self.cards if isinstance(c, Potion))
        weapons = sum(1 for c in self.cards if isinstance(c, Weapon))
        
        return DeckComposition(
            monsters=monsters,
            potions=potions,
            weapons=weapons
        )

    def to_bottom(self, cards: list[AnyCard]) -> None:
        for card in cards:
            self.cards.insert(0, card)
            self.bottomed_cards += 1


class GameState(BaseModel):
    player: Player
    deck: Deck
    room: Room
    discard_pile: list[AnyCard] = Field(default_factory=list)

    slain_monsters: list[Monster] = Field(default_factory=list)
    last_room_fled: bool = False

    @computed_field
    @property
    def total_slain_count(self) -> int:
        """ Returns the total number of monsters defeated so far."""
        return len(self.slain_monsters)
