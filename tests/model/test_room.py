import pytest
from pydantic import ValidationError
from scoundrel.models import Room, Monster, Potion, Suit

# --- Initialization & Basic Properties ---

def test_room_initialization_empty():
    """
    Checks if a room starts with default values: no cards and zero potions used.
    """
    room = Room()
    assert room.cards == []
    assert room.remaining == 0
    assert room.potions_used == 0

def test_room_initialization_with_cards():
    """
    Ensures that providing a list of cards correctly populates the room.
    """
    m1 = Monster(suit=Suit.SPADES, rank=10, name="Orc")
    m2 = Potion(suit=Suit.HEARTS, rank=5, name="Small Potion")
    room = Room(cards=[m1, m2], potions_used=1)
    
    assert room.remaining == 2
    assert room.potions_used == 1
    assert room.cards[0].card_id == "SPADES_10"

# --- Interaction Logic (The Core of Room) ---

def test_room_interacted_success():
    """
    Verifies that a card is correctly found and removed via its deterministic ID.
    """
    m1 = Monster(suit=Suit.SPADES, rank=10, name="Orc")
    m2 = Monster(suit=Suit.CLUBS, rank=5, name="Goblin")
    room = Room(cards=[m1, m2])
    
    # Remove the Orc
    room.interacted(m1)
    
    assert room.remaining == 1
    assert room.cards[0].card_id == "CLUBS_5"
    assert m1 not in room.cards

def test_room_interacted_raises_value_error_if_missing():
    """
    Ensures that trying to remove a card not present in the room raises a ValueError.
    """
    m1 = Monster(suit=Suit.SPADES, rank=10, name="In Room")
    m2 = Monster(suit=Suit.CLUBS, rank=5, name="Not In Room")
    room = Room(cards=[m1])
    
    with pytest.raises(ValueError, match="not found in current room"):
        room.interacted(m2)

def test_room_interacted_with_duplicate_rank_different_suit():
    """
    Critical test for deterministic IDs: Ensures that the correct suit is removed
    even if ranks are identical.
    """
    m_spades = Monster(suit=Suit.SPADES, rank=8, name="8 of Spades")
    m_clubs = Monster(suit=Suit.CLUBS, rank=8, name="8 of Clubs")
    room = Room(cards=[m_spades, m_clubs])
    
    # Remove Spades, Clubs must remain
    room.interacted(m_spades)
    assert room.remaining == 1
    assert room.cards[0].suit == Suit.CLUBS
    assert room.cards[0].card_id == "CLUBS_8"

# --- State Management (Potions) ---

def test_room_potions_used_increment():
    """
    Tests if the integer counter for potions used can be updated.
    The RulesEngine will use this to enforce limits.
    """
    room = Room()
    room.potions_used += 1
    assert room.potions_used == 1
    
    room.potions_used += 1
    assert room.potions_used == 2

# --- Validation & Edge Cases ---

def test_room_potions_used_validation():
    """
    Ensures that Pydantic enforces the 'greater or equal to 0' constraint.
    (Only works if Field(ge=0) is set in the model).
    """
    with pytest.raises(ValidationError):
        Room(potions_used=-1)

def test_room_serialization_cycle():
    """
    Ensures that a Room can be converted to a dict and back without losing data.
    """
    m1 = Monster(suit=Suit.SPADES, rank=14, name="Dragon")
    room = Room(cards=[m1], potions_used=2)