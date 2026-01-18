from scoundrel.models import Potion, Suit


# --- 1. Preview Tests ---

def test_preview_potion_full_healing(engine, empty_state):
    """Checks if potion provides full healing when HP is low."""
    empty_state.player.current_life = 10
    empty_state.player.max_life = 20
    potion = Potion(suit=Suit.HEARTS, rank=5, name="Small Potion")

    preview = engine.preview_potion(empty_state, potion)

    # 10 + 5 = 15, so 5 healing received
    assert preview.healing_received == 5


def test_preview_potion_capped_healing(engine, empty_state):
    """Checks if healing is capped at max_life."""
    empty_state.player.current_life = 18
    empty_state.player.max_life = 20
    potion = Potion(suit=Suit.HEARTS, rank=5, name="Small Potion")

    preview = engine.preview_potion(empty_state, potion)

    # 18 + 5 = 23 -> capped at 20, so only 2 healing received
    assert preview.healing_received == 2


def test_preview_second_potion_gives_zero(engine, empty_state):
    """
    Scoundrel Rule: Only the first potion in a room heals.
    Subsequent ones should preview 0 healing.
    """
    empty_state.player.current_life = 10
    empty_state.room.potions_used = 1  # One potion already used in this room
    potion = Potion(suit=Suit.HEARTS, rank=5, name="Second Potion")

    preview = engine.preview_potion(empty_state, potion)

    assert preview.healing_received == 0


# --- 2. Handle & State Tests ---

def test_handle_drink_potion_updates_hp_and_room(engine, empty_state):
    """Verifies state changes after drinking a potion."""
    empty_state.player.current_life = 10
    potion = Potion(suit=Suit.HEARTS, rank=7, name="Healing Draft")
    empty_state.room.cards.append(potion)

    # Act
    engine.handle_drink_potion(empty_state, potion)

    # Assert
    assert empty_state.player.current_life == 17
    assert empty_state.room.potions_used == 1
    assert potion not in empty_state.room.cards


def test_handle_second_potion_wastes_it(engine, empty_state):
    """
    Verifies that drinking a second potion removes it from the room
    but does NOT heal the player.
    """
    empty_state.player.current_life = 10
    empty_state.room.potions_used = 1
    potion = Potion(suit=Suit.HEARTS, rank=10, name="Wasted Potion")
    empty_state.room.cards.append(potion)

    # Act
    engine.handle_drink_potion(empty_state, potion)

    # Assert
    assert empty_state.player.current_life == 10  # No healing!
    assert empty_state.room.potions_used == 2
    assert potion not in empty_state.room.cards
