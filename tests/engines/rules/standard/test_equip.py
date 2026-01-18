import pytest
from scoundrel.models import Weapon, Suit, EquippedWeapon, Monster


def test_handle_equip_weapon_replaces_old_one(engine, empty_state):
    """
    Checks that equipping a new weapon replaces the current one
    and removes the card from the room.
    """
    # 1. Setup: Player already has an old sword equipped
    old_weapon = Weapon(suit=Suit.DIAMONDS, rank=4, name="Altes Schwert")
    empty_state.player.equipped = EquippedWeapon(weapon=old_weapon)

    # 2. New "Longsword" available in room
    new_weapon = Weapon(suit=Suit.DIAMONDS, rank=8, name="Langschwert")
    empty_state.room.cards.append(new_weapon)

    engine.handle_equip_weapon(empty_state, new_weapon)

    assert empty_state.player.equipped.weapon.protection == 8
    assert empty_state.player.equipped.weapon.name == "Langschwert"
    assert new_weapon not in empty_state.room.cards


def test_equip_weapon_clears_slain_monster_history(engine, empty_state):
    """
    Crucial Rule: When a new weapon is equipped, the history of
    slain monsters must be reset.
    """
    # 1. Setup: Weapon with history quipped
    old_weapon = Weapon(suit=Suit.DIAMONDS, rank=10, name="Meisterschwert")
    equipped = EquippedWeapon(weapon=old_weapon)
    goblin = Monster(suit=Suit.SPADES, rank=5, name="Goblin")
    equipped.slain_monsters.append(goblin)
    empty_state.player.equipped = equipped

    # 2. New Weapon inside the room
    new_weapon = Weapon(suit=Suit.DIAMONDS, rank=6, name="Dolch")
    empty_state.room.cards.append(new_weapon)

    engine.handle_equip_weapon(empty_state, new_weapon)

    # Newly equipped weapon has no history
    assert len(empty_state.player.equipped.slain_monsters) == 0
    # Lastly defeated monster is None
    assert empty_state.player.equipped.last_slain_monster is None


def test_cannot_equip_weapon_not_in_room(engine, empty_state):
    """
    Validation: You cannot equip a weapon that isn't in the current room.
    """
    weapon_outside = Weapon(suit=Suit.DIAMONDS, rank=5, name="Geister-Schwert")

    success = engine.can_equip_weapon(empty_state, weapon_outside)

    assert success is False
