import pytest
from scoundrel.models import Monster, Weapon, EquippedWeapon, Suit, GameState, Room


def test_preview_attack_bare_handed(engine, empty_state):
    """Checks that fighting without a weapon (use_weapon=False) deals full damage."""
    monster = Monster(suit=Suit.SPADES, rank=8, name="Ogre")
    
    # Act: Player chooses NOT to use a weapon
    preview = engine.preview_attack(empty_state, monster, use_weapon=False)
    
    # Assert: 8 damage expected
    assert preview.damage_taken == 8
    assert preview.is_lethal is False


def test_preview_attack_with_fresh_weapon(engine, empty_state):
    """A fresh weapon should reduce damage by its protection/rank value."""
    monster = Monster(suit=Suit.SPADES, rank=10, name="Demon")
    weapon_card = Weapon(suit=Suit.DIAMONDS, rank=6, name="Sword")
    
    # Setup: Equip the weapon (history is empty)
    empty_state.player.weapon = EquippedWeapon(weapon=weapon_card)
    
    # Act: Attack using the weapon
    preview = engine.preview_attack(empty_state, monster, use_weapon=True)
    
    # Assert: 10 (Monster) - 6 (Weapon) = 4 Damage
    assert preview.damage_taken == 4

def test_preview_attack_damage_clamped_at_zero(engine, empty_state):
    """If the weapon is stronger than the monster, damage should be 0, not negative."""
    monster = Monster(suit=Suit.SPADES, rank=4, name="Small Rat")
    weapon_card = Weapon(suit=Suit.DIAMONDS, rank=6, name="Sword")
    
    empty_state.player.weapon = EquippedWeapon(weapon=weapon_card)
    
    preview = engine.preview_attack(empty_state, monster, use_weapon=True)
    
    assert preview.damage_taken == 0

def test_preview_attack_weapon_ineffective_by_history(engine, empty_state):
    """
    Weapon only helps if current monster rank < last slain monster rank.
    If current is GREATER OR EQUAL, weapon provides 0 protection.
    """
    # Last slain monster was Rank 5
    m_old = Monster(suit=Suit.CLUBS, rank=5, name="Previous Foe")
    weapon_card = Weapon(suit=Suit.DIAMONDS, rank=7, name="Sword")
    empty_state.player.weapon = EquippedWeapon(weapon=weapon_card, slain_monsters=[m_old])
    
    # Current monster is Rank 6 (Stronger than the previous one!)
    m_new = Monster(suit=Suit.SPADES, rank=6, name="Current Foe")
    
    # Act
    preview = engine.preview_attack(empty_state, m_new, use_weapon=True)
    
    # Assert: Full damage (6) because the weapon is ineffective
    assert preview.damage_taken == 6

def test_preview_attack_lethality_flag(engine, empty_state):
    """Checks if the is_lethal flag correctly identifies a killing blow."""
    monster = Monster(suit=Suit.SPADES, rank=20, name="Death")
    empty_state.player.current_life = 15
    
    preview = engine.preview_attack(empty_state, monster, use_weapon=False)
    
    assert preview.damage_taken == 20
    assert preview.is_lethal is True


def test_can_attack_monster_in_room(engine, empty_state):
    """Checks that a monster can be attacked if it is actually in the room."""
    monster = Monster(suit=Suit.SPADES, rank=5, name="Goblin")
    empty_state.room.cards.append(monster)
    
    # Standard attack should be allowed
    assert engine.can_attack_monster(empty_state, monster, use_weapon=False) is True

def test_cannot_attack_monster_not_in_room(engine, empty_state):
    """
    Validation must fail if the monster object is not part of the 
    current room cards.
    """
    monster_in_room = Monster(suit=Suit.SPADES, rank=5, name="Goblin")
    monster_outside = Monster(suit=Suit.CLUBS, rank=10, name="Dragon")
    
    empty_state.room.cards.append(monster_in_room)
    
    # Attacking the dragon (not in room) must be False
    assert engine.can_attack_monster(empty_state, monster_outside, use_weapon=False) is False

def test_cannot_use_weapon_if_none_equipped(engine, empty_state):
    """
    Crucial for UI: Player cannot select 'use_weapon=True' 
    if they don't have a weapon.
    """
    monster = Monster(suit=Suit.SPADES, rank=5, name="Goblin")
    empty_state.room.cards.append(monster)
    
    # Player has no weapon (empty_state.player.weapon is None)
    assert engine.can_attack_monster(empty_state, monster, use_weapon=True) is False
    # But bare-handed is fine
    assert engine.can_attack_monster(empty_state, monster, use_weapon=False) is True

def test_can_use_weapon_if_equipped(engine, empty_state):
    """Standard case: Player has weapon and wants to use it."""
    monster = Monster(suit=Suit.SPADES, rank=5, name="Goblin")
    weapon_card = Weapon(suit=Suit.DIAMONDS, rank=4, name="Dagger")
    
    empty_state.room.cards.append(monster)
    empty_state.player.weapon = EquippedWeapon(weapon=weapon_card)
    
    assert engine.can_attack_monster(empty_state, monster, use_weapon=True) is True


def test_handle_attack_updates_player_health(engine, empty_state):
    """Verifies that health is actually reduced after an attack."""
    monster = Monster(suit=Suit.SPADES, rank=10, name="Ogre")
    empty_state.room.cards.append(monster)
    empty_state.player.current_life = 20
    
    # Act: Attack bare-handed (10 damage)
    engine.handle_monster_attack(empty_state, monster, use_weapon=False)
    
    # Assert
    assert empty_state.player.current_life == 10

def test_handle_attack_removes_monster_from_room(engine, empty_state):
    """Ensures the monster is moved from 'cards' to 'interacted_cards'."""
    monster = Monster(suit=Suit.SPADES, rank=5, name="Goblin")
    empty_state.room.cards.append(monster)
    
    # Act
    engine.handle_monster_attack(empty_state, monster, use_weapon=False)
    
    # Assert
    assert monster not in empty_state.room.cards

def test_handle_attack_updates_weapon_history(engine, empty_state):
    """
    Crucial Scoundrel Rule: Using a weapon must record the monster 
    to restrict future weapon use.
    """
    monster = Monster(suit=Suit.SPADES, rank=5, name="Goblin")
    weapon_card = Weapon(suit=Suit.DIAMONDS, rank=8, name="Sword")
    
    empty_state.room.cards.append(monster)
    empty_state.player.weapon = EquippedWeapon(weapon=weapon_card)
    
    # Act: Attack using the weapon
    engine.handle_monster_attack(empty_state, monster, use_weapon=True)
    
    # Assert
    # The monster must now be the 'last_slain_monster' in history
    assert len(empty_state.player.weapon.slain_monsters) == 1
    assert empty_state.player.weapon.slain_monsters[-1].rank == 5

def test_handle_attack_bare_handed_does_not_affect_weapon(engine, empty_state):
    """
    Strategy Check: If I fight bare-handed, my weapon history 
    should remain untouched.
    """
    monster = Monster(suit=Suit.SPADES, rank=5, name="Goblin")
    weapon_card = Weapon(suit=Suit.DIAMONDS, rank=8, name="Sword")
    
    empty_state.room.cards.append(monster)
    empty_state.player.weapon = EquippedWeapon(weapon=weapon_card) # Fresh weapon
    
    # Act: Attack with Fists
    engine.handle_monster_attack(empty_state, monster, use_weapon=False)
    
    # Assert: Weapon history is still empty
    assert len(empty_state.player.weapon.slain_monsters) == 0