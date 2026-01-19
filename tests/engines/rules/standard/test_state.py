import pytest
from scoundrel.models import Monster, Suit, Potion


# --- Game Over Logic Tests ---

def test_is_game_over_returns_none_if_alive(engine, empty_state):
    """
    The game should not be over if the player has more than 0 health.
    """
    empty_state.player.current_life = 1
    assert engine.is_game_over(empty_state) is None


def test_is_game_over_calculates_penalty_score(engine, empty_state):
    """
    When the player is dead (HP <= 0), the score is HP minus the
    total strength of monsters remaining in the deck.
    """
    # Setup player death
    empty_state.player.current_life = -2

    # Setup deck with monsters and non-monster cards
    empty_state.deck.cards = [
        Monster(suit=Suit.SPADES, rank=10, name="Ogre"),  # Strength 10
        Monster(suit=Suit.CLUBS, rank=4, name="Goblin"),  # Strength 4
        Potion(suit=Suit.HEARTS, rank=5, name="Health Pot")  # Should be ignored
    ]

    score = engine.is_game_over(empty_state)

    # Expected: -2 (HP) - 14 (Monster Strength) = -16
    assert score == -16


def test_is_game_over_zero_hp_no_monsters(engine, empty_state):
    """
    If the player dies but no monsters are left in the deck,
    the score should just be the player's HP.
    """
    empty_state.player.current_life = 0
    empty_state.deck.cards = [Potion(suit=Suit.HEARTS, rank=5, name="Pot")]

    score = engine.is_game_over(empty_state)
    assert score == 0


# --- Victory Logic Tests ---

def test_is_victory_returns_hp_when_dungeon_cleared(engine, empty_state):
    """
    Victory is achieved when both deck and room are empty.
    The score should be the player's remaining life.
    """
    empty_state.player.current_life = 15
    empty_state.deck.cards = []
    empty_state.room.cards = []

    score = engine.is_victory(empty_state)
    assert score == 15


def test_is_victory_returns_hp_when_dungeon_cleared_2(engine, empty_state):
    """
    Victory is achieved when both deck and room are empty.
    The score should be the player's remaining life.
    """
    empty_state.player.current_life = 15
    empty_state.deck.cards = []
    empty_state.room.cards = [Monster(suit=Suit.SPADES, rank=2, name="M")]

    score = engine.is_victory(empty_state)
    assert score == 15


def test_is_victory_returns_hp_when_dungeon_cleared_and_bonus_potion(engine, empty_state):
    """
    Victory is achieved when both deck and room are empty.
    The score should be the player's remaining life.
    """
    empty_state.player.current_life = 15
    empty_state.deck.cards = []
    empty_state.room.cards = [Potion(suit=Suit.HEARTS, rank=10, name="M")]

    score = engine.is_victory(empty_state)
    assert score == 25


def test_is_victory_returns_none_if_deck_not_empty(engine, empty_state):
    """
    Victory condition should not be met if there are still cards in the deck.
    """
    empty_state.player.current_life = 20
    empty_state.deck.cards = [Monster(suit=Suit.SPADES, rank=2, name="M")]
    empty_state.room.cards = []

    assert engine.is_victory(empty_state) is None


def test_is_victory_returns_none_if_room_not_empty(engine, empty_state):
    """
    Victory condition should not be met if there are still cards in the room.
    """
    empty_state.player.current_life = 20
    empty_state.deck.cards = []
    empty_state.room.cards = [Monster(suit=Suit.SPADES, rank=2, name="M"), Monster(suit=Suit.SPADES, rank=3, name="M")]

    assert engine.is_victory(empty_state) is None
