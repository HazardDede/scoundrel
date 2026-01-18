import pytest
from scoundrel.models import GameState, Player, Room, Deck
from scoundrel.engines import StandardRulesEngine


@pytest.fixture
def engine():
    return StandardRulesEngine()


@pytest.fixture
def player():
    return Player(current_life=20, max_life=20)


@pytest.fixture
def empty_state(player):
    return GameState(
        player=player,
        room=Room(cards=[]),
        deck=Deck(cards=[])
    )
