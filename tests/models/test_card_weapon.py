import pytest
from pydantic import TypeAdapter
from scoundrel.models import Weapon, Suit, AnyCard


# --- Specific Weapon Tests ---

def test_weapon_initialization():
    """
    Ensures that a weapon is correctly initialized with its specific type and protection.
    """
    weapon = Weapon(suit=Suit.DIAMONDS, rank=12, name="Queen of Diamonds")
    
    # Check the literal type for the discriminator
    assert weapon.type == "weapon"
    # Check if protection maps to rank
    assert weapon.protection == 12


def test_weapon_inheritance_from_card():
    """
    Verifies that Weapon correctly inherits card_id and frozen state from Card.
    """
    weapon = Weapon(suit=Suit.DIAMONDS, rank=14, name="Ace of Diamonds")
    assert weapon.card_id == "DIAMONDS_14"
    
    # Verify that the frozen config is active (inherited from Card)
    with pytest.raises(Exception): 
        weapon.rank = 2


def test_weapon_in_anycard_context():
    """
    Tests if the AnyCard Union correctly parses a Weapon from dictionary data.
    """
    data = {
        "suit": "DIAMONDS",
        "rank": 9,
        "name": "Steel Sword",
        "type": "weapon"
    }
    adapter = TypeAdapter(AnyCard)
    obj = adapter.validate_python(data)
    
    # This is crucial for the RulesEngine to later work with the correct class
    assert isinstance(obj, Weapon)
    assert obj.protection == 9


@pytest.mark.parametrize("rank", [2, 10, 14])
def test_weapon_protection_mapping(rank):
    """
    Validates the contract that protection value equals the card rank.
    """
    weapon = Weapon(suit=Suit.DIAMONDS, rank=rank, name="Test Weapon")
    assert weapon.protection == rank