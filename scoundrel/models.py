"""
Core models for the Scoundrel game engine.

This module defines the data structures for cards, players, rooms, and the game state
using Pydantic for validation and immutability where required.
"""

import random
from enum import Enum
from typing import Literal, Optional, Annotated, Union, Final

from pydantic import BaseModel, Field, computed_field, ConfigDict

from scoundrel import exc

# --- Constants for type-safe discriminators ---
CONST_MONSTER: Final = "monster"
CONST_POTION: Final = "potion"
CONST_WEAPON: Final = "weapon"


HighScore = int
Rank = int


class Suit(str, Enum):
    """Enumeration of card suits and their associated gameplay mechanics."""
    SPADES = "SPADES"      # Pik (Monster)
    CLUBS = "CLUBS"        # Kreuz (Monster)
    DIAMONDS = "DIAMONDS"  # Karo (Waffen)
    HEARTS = "HEARTS"      # Herz (Heiltränke)


class ActionPreview(BaseModel):
    """
    Provides a projection of the consequences of a potential player action.

    Used by the UI or AI to calculate damage and lethality before committing
    to a move.
    """
    damage_taken: int = 0
    healing_received: int = 0
    is_lethal: bool = False  # Would this action kill the player?


class Card(BaseModel):
    """
    Abstract base representation of a game card.

    Cards are frozen to ensure hashability and prevent accidental state
    mutation during gameplay or theming.
    """
    # This makes the card immutable and hashable
    model_config = ConfigDict(frozen=True)

    suit: Suit
    rank: Rank  # 2-10, 11 (J), 12 (Q), 13 (K), 14 (A)
    name: str
    type: str  # Override in child classes
    emoji: Optional[str] = None

    @computed_field
    def card_id(self) -> str:
        """Deterministic unique identifier based on suit and rank."""
        # Deterministic ID based on suit and rank (e.g., "SPADES_14")
        return f"{self.suit.value.upper()}_{self.rank}"

    def __str__(self) -> str:
        return f"{self.name} ({self.card_id})"

    def __repr__(self) -> str:
        return f"Card(id={self.card_id}, type={self.type})"


class Monster(Card):
    """Representing an enemy that deals damage based on its rank."""
    type: Literal["monster"] = CONST_MONSTER

    @property
    def strength(self) -> int:
        """The damage value of the monster."""
        # Base strength is tied to rank, but easily modifiable later
        return self.rank


class Potion(Card):
    """Representing a healing item that restores health."""
    type: Literal["potion"] = CONST_POTION

    @property
    def potency(self) -> int:
        """The amount of health restored by this potion."""
        return self.rank


class Weapon(Card):
    """Representing equipment used to mitigate monster damage."""
    type: Literal["weapon"] = CONST_WEAPON

    @property
    def protection(self) -> int:
        """The amount of protection / power this weapon offers."""
        return self.rank


# Type alias for Pydantic polymorphic parsing
AnyCard = Annotated[Union[Monster, Potion, Weapon], Field(discriminator='type')]


class EquippedWeapon(BaseModel):
    """
    Container for the player's currently active weapon and its history.

    In Scoundrel, weapons track the last slain monster to enforce the
    rule that you cannot slay a monster of equal or higher rank than the previous one.
    """
    weapon: Weapon
    slain_monsters: list[Monster] = Field(default_factory=list)

    @computed_field
    def last_slain_monster(self) -> Optional[Monster]:
        """The most recently defeated monster using this specific weapon."""
        return self.slain_monsters[-1] if self.slain_monsters else None


class Player(BaseModel):
    """Representing the user's state, health, and equipment."""
    max_life: int = 20
    current_life: int = 20

    equipped: Optional[EquippedWeapon] = None

    @property
    def is_dead(self) -> bool:
        """True if current_life reaches zero."""
        return self.current_life <= 0

    @property
    def has_weapon(self) -> bool:
        """Check if the player has an active EquippedWeapon."""
        return self.equipped is not None

    def heal(self, amount: int) -> None:
        """Restore health up to max_life."""
        if amount < 0:
            raise ValueError("Positive value expected")
        self.current_life = min(self.max_life, self.current_life + amount)

    def take_damage(self, amount: int) -> None:
        """Reduce health, clamped at zero."""
        if amount < 0:
            raise ValueError("Positive value expected")
        self.current_life = max(0, self.current_life - amount)


class Room(BaseModel):
    """
    Representing the current set of cards (usually 4) presented to the player.

    A room is cleared when the player interacts with cards or flees.
    """
    cards: list[AnyCard] = Field(default_factory=list)
    potions_used: int = Field(0, ge=0)

    @property
    def remaining(self) -> int:
        """Count of cards currently left in the room."""
        return len(self.cards)

    def exists(self, card: AnyCard) -> bool:
        """Check if a card with the same ID is present in the room."""
        return card.card_id in [c.card_id for c in self.cards]

    def interacted(self, card: AnyCard) -> None:
        """
        Remove a card from the room upon interaction.

        Note: Comparison is done via card_id as card instances may vary
        due to theming/copying.
        """
        # Find index and card at once
        try:
            idx, _ = next(
                ((i, c) for i, c in enumerate(self.cards) if c.card_id == card.card_id)
            )
            self.cards.pop(idx)  # pylint: disable=no-member
        except StopIteration:
            raise ValueError(f"Card {card.card_id} not found in current room.")  # pylint: disable=raise-missing-from


class DeckComposition(BaseModel):
    """The distribution of card types currently inside a Deck."""
    monsters: int
    potions: int
    weapons: int

    @property
    def total(self) -> int:
        """The total sum of all cards in this composition."""
        return self.monsters + self.potions + self.weapons


class Deck(BaseModel):
    """
    Representing the draw pile.

    Manages drawing, shuffling, and returning cards to the bottom.
    """
    cards: list[AnyCard] = Field(default_factory=list)
    bottomed_cards: int = 0

    def shuffle(self) -> None:
        """Randomize the order of remaining cards in the deck."""
        random.shuffle(self.cards)

    def draw(self) -> AnyCard:
        """Remove and return the top card (last element in the list)."""
        if len(self.cards) < 1:
            raise exc.DeckEmptyError("Deck is empty")

        return self.cards.pop()  # pylint: disable=no-member

    @property
    def remaining(self) -> int:
        """Number of cards left in the draw pile."""
        return len(self.cards)

    @property
    def is_empty(self) -> bool:
        """True if no cards are left to draw."""
        return len(self.cards) == 0

    @property
    def composition(self) -> DeckComposition:
        """Analyzes the current state of the deck and returns the counts of each card type."""
        monsters = sum(1 for c in self.cards if isinstance(c, Monster))
        potions = sum(1 for c in self.cards if isinstance(c, Potion))
        weapons = sum(1 for c in self.cards if isinstance(c, Weapon))

        return DeckComposition(
            monsters=monsters,
            potions=potions,
            weapons=weapons
        )

    def to_bottom(self, cards: list[AnyCard]) -> None:
        """Place cards at the start of the list and track the count."""
        for card in cards:
            self.cards.insert(0, card)  # pylint: disable=no-member
            self.bottomed_cards += 1


class GameState(BaseModel):
    """
    The root aggregate containing the complete status of a Scoundrel session.

    This is the primary object for serialization and state management.
    """
    player: Player
    deck: Deck
    room: Room
    discard_pile: list[AnyCard] = Field(default_factory=list)

    slain_monsters: list[Monster] = Field(default_factory=list)
    last_room_fled: bool = False

    @computed_field
    def total_slain_count(self) -> int:
        """The running total of all monsters defeated across the session."""
        return len(self.slain_monsters)
