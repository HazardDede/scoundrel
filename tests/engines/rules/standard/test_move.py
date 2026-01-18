from scoundrel.models import Monster, Suit


# --- 1. next_room_available ---

def test_next_room_available_when_empty(engine, empty_state):
    """Room should be refillable if it has 0 cards."""
    empty_state.room.cards = []
    assert engine.next_room_available(empty_state) is True


def test_next_room_available_with_one_card(engine, empty_state):
    """Room should be refillable if exactly 1 card remains (Scoundrel rule)."""
    monster = Monster(suit=Suit.SPADES, rank=5, name="Lonely Goblin")
    empty_state.room.cards = [monster]
    assert engine.next_room_available(empty_state) is True


def test_next_room_not_available_with_two_cards(engine, empty_state):
    """Room cannot be refilled if 2 or more cards are still present."""
    m1 = Monster(suit=Suit.SPADES, rank=5, name="Goblin 1")
    m2 = Monster(suit=Suit.SPADES, rank=6, name="Goblin 2")
    empty_state.room.cards = [m1, m2]
    assert engine.next_room_available(empty_state) is False


# --- 2. handle_next_room ---

def test_handle_next_room_fills_to_four_cards(engine, empty_state):
    """Verifies that handle_next_room draws exactly 4 cards into an empty room."""
    # Setup deck with 10 cards
    for i in range(10):
        empty_state.deck.cards.append(Monster(suit=Suit.SPADES, rank=i + 2, name=f"M{i}"))

    empty_state.room.cards = []

    # Act
    engine.handle_next_room(empty_state)

    # Assert
    assert len(empty_state.room.cards) == 4
    assert empty_state.deck.remaining == 6


def test_handle_next_room_resets_flee_flag(engine, empty_state):
    """
    Crucial Rule: Entering a room normally (not by fleeing)
    resets the last_room_fled flag.
    """
    empty_state.last_room_fled = True
    # Room has 1 card left (triggering availability)
    empty_state.room.cards = [Monster(suit=Suit.SPADES, rank=2, name="Leftover")]

    engine.handle_next_room(empty_state)
    assert empty_state.last_room_fled is False


def test_handle_next_room_resets_potion_counter(engine, empty_state):
    """Verifies that the potion limit is reset for the new room."""
    empty_state.room.potions_used = 1
    empty_state.room.cards = []

    engine.handle_next_room(empty_state)

    assert empty_state.room.potions_used == 0
