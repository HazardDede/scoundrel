import pytest
from pydantic import TypeAdapter
from scoundrel.models import Monster, Suit, AnyCard


# --- Specific Monster Tests ---

def test_monster_initialization():
    """
    Ensures that a monster is correctly initialized with its specific type and strength.
    """
    monster = Monster(suit=Suit.SPADES, rank=13, name="King of Spades")
    
    # Check if the literal type is correctly set
    assert monster.type == "monster"
    # Check if the strength property correctly maps to rank
    assert monster.strength == 13

def test_monster_is_frozen_by_inheritance():
    """
    Ensures that the frozen config from Card is correctly inherited by Monster.
    """
    monster = Monster(suit=Suit.CLUBS, rank=5, name="Five of Clubs")
    
    with pytest.raises(Exception): # Pydantic's FrozenInstanceError
        monster.rank = 10

def test_monster_in_anycard_context():
    """
    Verifies that the Annotated Union (AnyCard) correctly identifies a Monster dictionary.
    """
    monster_data = {
        "suit": "SPADES",
        "rank": 14,
        "name": "Ace of Spades",
        "type": "monster"
    }
    
    # Use TypeAdapter to validate the Union
    adapter = TypeAdapter(AnyCard)
    obj = adapter.validate_python(monster_data)
    
    assert isinstance(obj, Monster)
    assert obj.strength == 14


@pytest.mark.parametrize("rank", [2, 10, 14])
def test_monster_strength_calculation(rank):
    """
    Specifically tests the rank-to-strength mapping. 
    If you change the formula later, this test will point it out.
    """
    monster = Monster(suit=Suit.CLUBS, rank=rank, name="Test Monster")
    # Current logic: strength == rank
    assert monster.strength == rank