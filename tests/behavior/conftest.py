import pytest
from pytest_bdd import given, when, then, parsers

from scoundrel import models
from scoundrel.builders import StandardDeckBuilder, DeckFlavor
from scoundrel.engines import StandardRulesEngine


@pytest.fixture
def engine():
    return StandardRulesEngine()


@pytest.fixture
def state():
    deck = StandardDeckBuilder(flavor=DeckFlavor.QUICK).build()
    return models.GameState(
        player=models.Player(current_life=20),
        deck=deck,
        room=models.Room(cards=[])
    )


@given(parsers.parse("a player with {health:d} health"))
def player_health(state, health):
    state.player.current_life = health


@given(parsers.parse('an equipped weapon called "{weapon}" of rank {rank:d}'))
def player_weapon(state, weapon, rank):
    weapon = models.Weapon(suit=models.Suit.DIAMONDS, rank=rank, name=weapon)
    state.player.equipped = models.EquippedWeapon(weapon=weapon)


@given(parsers.parse('the room containing a "{monster}" potion of rank {rank:d}'))
def potion_in_room(state, potion, rank):
    potion = models.Potion(suit=models.Suit.HEARTS, rank=rank, name=potion)
    state.room.cards.append(potion)


@given(parsers.parse('the room containing a "{monster}" monster of rank {rank:d}'))
def monster_in_room(state, monster, rank):
    monster = models.Monster(suit=models.Suit.CLUBS, rank=rank, name=monster)
    state.room.cards.append(monster)


@when(parsers.parse('the player attacks the "{monster}" bare-handed'))
def attack_monster_bare_handed(state, engine, monster):
    monster_card = next(c for c in state.room.cards if c.name == monster)

    assert monster_card is not None, "The monster is not inside the room"
    assert engine.can_attack_monster(state, monster_card, use_weapon=False)
    engine.handle_monster_attack(state, monster_card, use_weapon=False)


@when(parsers.parse('the player attacks the "{monster}" using his gear'))
def attack_monster_equipment(state, engine, monster):
    monster_card = next(c for c in state.room.cards if c.name == monster)

    assert monster_card is not None, "The monster is not inside the room"
    assert engine.can_attack_monster(state, monster_card, use_weapon=True)
    engine.handle_monster_attack(state, monster_card, use_weapon=True)


@then(parsers.parse("the player should have {health:d} health remaining"))
def check_player_health(state, health):
    assert state.player.current_life == health


@then(parsers.parse('the "{monster}" should be removed from the room'))
def check_room_monster_negative(state, monster):
    try:
        next(c for c in state.room.cards if c.name == monster)
        assert False, "Monster is still in the room"
    except StopIteration:
        pass


@then(parsers.parse('the "{monster}" should still be in the room'))
def check_room_monster_positive(state, monster):
    try:
        next(c for c in state.room.cards if c.name == monster)
    except StopIteration:
        assert False, "Monster not in the room"


@then(parsers.parse('the weapons last slain monster should be a "{monster}" of rank {rank:d}'))
def check_weapon_last_slain(state, monster, rank):
    assert state.player.has_weapon, "Player does not have a weapon equipped!"
    last_monster = state.player.equipped.last_slain_monster

    assert last_monster is not None, "The weapon has no combat history (no monsters slain)."
    assert last_monster.name == monster, f"Expected {monster}, but found {last_monster.name}."
    assert last_monster.rank == rank, f"Expected rank {rank}, but found {last_monster.rank}."


@then(parsers.parse('the equipped weapon should be unused'))
def check_weapon_unused(state):
    assert state.player.has_weapon, "Player does not have a weapon equipped!"
    last_monster = state.player.equipped.last_slain_monster

    assert last_monster is None


@then(parsers.parse('the "{monster}" cannot be attacked using the gear'))
def check_attack_not_possible(state, engine, monster):
    try:
        monster_card = next(c for c in state.room.cards if c.name == monster)
        assert not engine.can_attack_monster(state, monster_card, use_weapon=True)
    except StopIteration:
        assert False, "Monster not in the room"
