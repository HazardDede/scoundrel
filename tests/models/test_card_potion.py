import pytest
from pydantic import TypeAdapter
from scoundrel.models import Potion, Suit, AnyCard


# --- Specific Potion Tests ---

def test_potion_initialization():
    """
    Ensures that a potion is correctly initialized with its specific type and potency.
    """
    potion = Potion(suit=Suit.HEARTS, rank=10, name="Standard Healing Potion")
    
    # Check the literal type for the discriminator
    assert potion.type == "potion"
    # Check if potency maps to rank
    assert potion.potency == 10

def test_potion_inheritance_from_card():
    """
    Verifies that Potion correctly inherits card_id and frozen state.
    """
    potion = Potion(suit=Suit.HEARTS, rank=14, name="Holy Grail")
    assert potion.card_id == "HEARTS_14"
    
    with pytest.raises(Exception): # FrozenInstanceError
        potion.rank = 2

def test_potion_in_anycard_context():
    """
    Tests if the AnyCard Union correctly parses a Potion from dictionary data.
    """
    data = {
        "suit": "Hearts",
        "rank": 7,
        "name": "Medium Potion",
        "type": "potion"
    }
    adapter = TypeAdapter(AnyCard)
    obj = adapter.validate_python(data)
    
    assert isinstance(obj, Potion)
    assert obj.potency == 7

@pytest.mark.parametrize("rank", [2, 5, 14])
def test_potion_potency_mapping(rank):
    """
    Validates the contract that potency equals rank for all potions.
    """
    potion = Potion(suit=Suit.HEARTS, rank=rank, name="Test Potion")
    assert potion.potency == rank