import pytest
from scoundrel.models import EquippedWeapon, Weapon, Monster, Suit

# --- EquippedWeapon Logic Tests ---

def test_equipped_weapon_initialization():
    """
    Prüft, ob eine Waffe korrekt angelegt wird und der Monster-Stack leer startet.
    """
    weapon_card = Weapon(suit=Suit.DIAMONDS, rank=10, name="Bastardschwert")
    equipped = EquippedWeapon(weapon=weapon_card)
    
    assert equipped.weapon.rank == 10
    assert len(equipped.slain_monsters) == 0
    assert equipped.last_slain_monster is None

def test_last_monster_property():
    """
    Prüft, ob last_monster immer das aktuellste Monster aus dem Stack liefert.
    """
    weapon_card = Weapon(suit=Suit.DIAMONDS, rank=12, name="Meisterschwert")
    equipped = EquippedWeapon(weapon=weapon_card)
    
    # Erstes Monster besiegen
    m1 = Monster(suit=Suit.SPADES, rank=8, name="Goblin")
    equipped.slain_monsters.append(m1)
    assert equipped.last_slain_monster == m1
    assert equipped.last_slain_monster.rank == 8
    
    # Zweites Monster besiegen
    m2 = Monster(suit=Suit.CLUBS, rank=5, name="Skelett")
    equipped.slain_monsters.append(m2)
    assert equipped.last_slain_monster == m2
    assert equipped.last_slain_monster.rank == 5
    
    # Prüfen, ob der gesamte Stack noch da ist
    assert len(equipped.slain_monsters) == 2

def test_equipped_weapon_serialization():
    """
    Stellt sicher, dass der gesamte Stack serialisiert wird.
    """
    weapon_card = Weapon(suit=Suit.DIAMONDS, rank=14, name="Excalibur")
    equipped = EquippedWeapon(weapon=weapon_card)
    m1 = Monster(suit=Suit.SPADES, rank=10, name="Ork")
    equipped.slain_monsters.append(m1)
    
    data = equipped.model_dump()
    assert data["weapon"]["rank"] == 14
    assert len(data["slain_monsters"]) == 1
    assert data["slain_monsters"][0]["rank"] == 10