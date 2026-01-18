from scoundrel.models import Monster, Suit


# --- Room Availability Tests ---

def test_next_room_available_when_empty(engine, empty_state):
    """Room should be refillable if it contains no cards."""
    empty_state.room.cards = []
    assert engine.next_room_available(empty_state) is True


def test_next_room_available_with_one_card(engine, empty_state):
    """Room should be refillable if exactly one card remains."""
    monster = Monster(suit=Suit.SPADES, rank=5, name="Last Monster")
    empty_state.room.cards = [monster]
    assert engine.next_room_available(empty_state) is True


def test_next_room_not_available_with_two_cards(engine, empty_state):
    """Refilling is forbidden if two or more cards are still present."""
    m1 = Monster(suit=Suit.SPADES, rank=5, name="Goblin A")
    m2 = Monster(suit=Suit.SPADES, rank=6, name="Goblin B")
    empty_state.room.cards = [m1, m2]
    assert engine.next_room_available(empty_state) is False


# --- Next Room Handling Tests ---

def test_handle_next_room_fills_to_four_cards(engine, empty_state):
    """Ensures handle_next_room draws cards until the room reaches 4 cards."""
    # Populate deck with dummy cards
    for i in range(10):
        empty_state.deck.cards.append(Monster(suit=Suit.SPADES, rank=i + 2, name=f"M{i}"))

    empty_state.room.cards = []

    # Act
    engine.handle_next_room(empty_state)

    # Assert
    assert len(empty_state.room.cards) == 4
    assert empty_state.deck.remaining == 6


def test_handle_next_room_resets_flee_flag(engine, empty_state):
    """Entering a new room after interaction resets the flee flag."""
    empty_state.last_room_fled = True
    # Room has 1 card left, triggering a normal room transition
    empty_state.room.cards = [Monster(suit=Suit.SPADES, rank=2, name="Leftover")]

    # Act
    engine.handle_next_room(empty_state)

    # Assert
    assert empty_state.last_room_fled is False


# --- Flee Logic Tests ---

def test_can_flee_room_validation(engine, empty_state):
    """Validates requirements: room must be full and no flee in previous turn."""
    # Case 1: Full room, first time fleeing
    empty_state.room.cards = [Monster(suit=Suit.SPADES, rank=5, name=str(i)) for i in range(4)]
    empty_state.last_room_fled = False
    assert engine.can_flee_room(empty_state) is True

    # Case 2: Room not full
    empty_state.room.cards.pop()
    assert engine.can_flee_room(empty_state) is False

    # Case 3: Full room but fled last time
    empty_state.room.cards.append(Monster(suit=Suit.SPADES, rank=5, name="4th"))
    empty_state.last_room_fled = True
    assert engine.can_flee_room(empty_state) is False


def test_handle_flee_room_behavior(engine, empty_state):
    """Verifies cards are moved to deck bottom and state is updated correctly."""
    m1 = Monster(suit=Suit.SPADES, rank=13, name="King")
    empty_state.room.cards = [m1, m1, m1, m1]
    empty_state.deck.cards = [Monster(suit=Suit.CLUBS, rank=2, name="DeckCard")]
    empty_state.last_room_fled = False

    # Act
    engine.handle_flee_room(empty_state)

    # Assert
    assert len(empty_state.room.cards) == 0
    assert empty_state.last_room_fled is True
    # Verify card was moved to the bottom (index 0)
    assert empty_state.deck.cards[0].name == "King"
