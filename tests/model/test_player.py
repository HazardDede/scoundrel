import pytest
from pydantic import ValidationError
from scoundrel.models import Player, Weapon, EquippedWeapon, Suit

# --- Health Logic Tests ---

def test_player_initial_state():
    """
    Ensures a new player starts with full health and no weapon.
    """
    player = Player()
    assert player.current_life == 20
    assert player.max_life == 20
    assert player.weapon is None
    assert player.is_dead is False

def test_player_take_damage():
    """
    Tests if taking damage reduces health but doesn't go below 0.
    """
    player = Player(current_life=10)
    player.take_damage(5)
    assert player.current_life == 5
    
    player.take_damage(10) # Overkill
    assert player.current_life == 0
    assert player.is_dead is True

def test_player_heal():
    """
    Tests if healing increases health but doesn't exceed max_life.
    """
    player = Player(current_life=10)
    player.heal(5)
    assert player.current_life == 15
    
    player.heal(10) # Overheal
    assert player.current_life == 20 # Should be capped at max_life

def test_negative_values_raise_error():
    """
    Ensures that healing or taking damage with negative values raises a ValueError.
    """
    player = Player()
    with pytest.raises(ValueError, match="Positive value expected"):
        player.heal(-5)
    with pytest.raises(ValueError, match="Positive value expected"):
        player.take_damage(-5)

# --- Weapon Assignment Tests ---

def test_player_equip_weapon():
    """
    Tests if a weapon can be assigned to the player.
    """
    player = Player()
    # Mocking a weapon card and its equipped state
    weapon_card = Weapon(suit=Suit.DIAMONDS, rank=10, name="Longsword")
    equipped = EquippedWeapon(weapon=weapon_card)
    
    player.weapon = equipped
    assert player.weapon.weapon.protection == 10
    assert player.weapon.last_slain_monster is None

# --- Serialization Test ---

def test_player_serialization():
    """
    Ensures the player state (including weapon) can be serialized.
    """
    weapon_card = Weapon(suit=Suit.DIAMONDS, rank=8, name="Dagger")
    player = Player(current_life=15, weapon=EquippedWeapon(weapon=weapon_card))
    
    data = player.model_dump()
    assert data["current_life"] == 15
    assert data["weapon"]["weapon"]["rank"] == 8