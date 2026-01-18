import pytest

from scoundrel import exc
from scoundrel.models import Deck, Monster, Suit, Potion, Weapon, DeckComposition

# --- Deck Logic Tests ---

def test_deck_initial_state():
    """Checks if the deck starts with the provided cards and correct counts."""
    m1 = Monster(suit=Suit.SPADES, rank=10, name="Monster 1")
    m2 = Monster(suit=Suit.CLUBS, rank=5, name="Monster 2")
    deck = Deck(cards=[m1, m2])
    
    assert deck.remaining == 2
    assert deck.is_empty is False

def test_deck_draw_success():
    """Ensures drawing a card removes it from the top (end of list)."""
    m1 = Monster(suit=Suit.SPADES, rank=10, name="Bottom Card")
    m2 = Monster(suit=Suit.CLUBS, rank=5, name="Top Card")
    deck = Deck(cards=[m1, m2])
    
    drawn = deck.draw()
    assert drawn.card_id == "CLUBS_5"
    assert deck.remaining == 1
    assert deck.cards[0].card_id == "SPADES_10"

def test_deck_draw_empty_raises_error():
    """Ensures an exception is raised when drawing from an empty deck."""
    deck = Deck(cards=[])
    with pytest.raises(exc.DeckEmptyError):
        deck.draw()

def test_deck_to_bottom():
    """
    Tests the fleeing mechanic: cards are moved to the bottom of the deck.
    In our implementation, index 0 is the bottom.
    """
    m1 = Monster(suit=Suit.SPADES, rank=2, name="Card 1")
    m2 = Monster(suit=Suit.CLUBS, rank=3, name="Card 2")
    deck = Deck(cards=[m1, m2])
    
    fleeing_cards = [
        Monster(suit=Suit.HEARTS, rank=10, name="Fleeing 1"),
        Monster(suit=Suit.DIAMONDS, rank=5, name="Fleeing 2")
    ]
    
    deck.to_bottom(fleeing_cards)
    
    # Check total count
    assert deck.remaining == 4
    # Check if they are at the bottom (index 0 and 1)
    # Note: to_bottom inserts at 0, so the last one in the loop becomes index 0
    assert deck.cards[0].rank == 5  # Last inserted
    assert deck.cards[1].rank == 10
    assert deck.bottomed_cards == 2

def test_deck_shuffle(monkeypatch):
    """
    Tests if shuffle is called. Since random is used, we check if the 
    order changes or simply mock the random.shuffle.
    """
    cards = [Monster(suit=Suit.SPADES, rank=r, name=str(r)) for r in range(2, 10)]
    deck = Deck(cards=list(cards))
    
    deck.shuffle()
    # While it's mathematically possible to shuffle into the same order, 
    # for 8 cards it's highly unlikely.
    assert len(deck.cards) == 8
    # We check if the sequence is different from the original
    assert [c.rank for c in deck.cards] != [r for r in range(2, 10)]


# --- Composition ---

def test_deck_composition_initial_calculation():
    """
    Tests if the composition correctly counts various card types upon creation.
    """
    cards = [
        Monster(suit=Suit.SPADES, rank=10, name="Orc"),
        Monster(suit=Suit.CLUBS, rank=5, name="Goblin"),
        Potion(suit=Suit.HEARTS, rank=8, name="Health Potion"),
        Weapon(suit=Suit.DIAMONDS, rank=3, name="Rusty Dagger")
    ]
    deck = Deck(cards=cards)
    
    comp = deck.composition
    
    assert isinstance(comp, DeckComposition)
    assert comp.monsters == 2
    assert comp.potions == 1
    assert comp.weapons == 1
    assert comp.total == 4

def test_deck_composition_after_drawing():
    """
    Ensures that drawing a card immediately updates the composition stats.
    """
    # Setup with 1 Monster and 1 Potion
    m1 = Monster(suit=Suit.SPADES, rank=10, name="Orc")
    p1 = Potion(suit=Suit.HEARTS, rank=8, name="Potion")
    deck = Deck(cards=[m1, p1]) # p1 is on top (index -1)
    
    # Initial check
    assert deck.composition.potions == 1
    assert deck.composition.total == 2
    
    # Draw the potion
    drawn_card = deck.draw()
    assert isinstance(drawn_card, Potion)
    
    # Composition must update
    new_comp = deck.composition
    assert new_comp.potions == 0
    assert new_comp.monsters == 1
    assert new_comp.total == 1

def test_deck_composition_empty_deck():
    """
    Verifies that an empty deck returns zero for all composition fields.
    """
    deck = Deck(cards=[])
    comp = deck.composition
    
    assert comp.total == 0
    assert comp.monsters == 0
    assert comp.potions == 0
    assert comp.weapons == 0

def test_deck_composition_is_read_only_by_nature():
    """
    Since composition is a @property, it shouldn't be directly settable.
    """
    deck = Deck(cards=[])
    with pytest.raises(AttributeError):
        # This should fail because 'composition' has no setter
        deck.composition = "something else"

# --- Serialization Test ---

def test_deck_serialization():
    """Ensures the deck state and bottomed_cards counter are preserved."""
    deck = Deck(cards=[Monster(suit=Suit.SPADES, rank=10, name="M")], bottomed_cards=5)
    data = deck.model_dump()
    
    assert data["bottomed_cards"] == 5
    assert len(data["cards"]) == 1