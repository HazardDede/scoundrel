import pytest
from scoundrel.models import GameState, Player, Deck, Room, Monster, Suit

# --- GameState Logic Tests ---

def test_gamestate_initialization():
    """
    Überprüft, ob ein neues Spiel korrekt mit allen Sub-Modellen startet.
    """
    player = Player()
    deck = Deck()
    room = Room()
    state = GameState(player=player, deck=deck, room=room)
    
    assert state.player.current_life == 20
    assert state.total_slain_count == 0
    assert state.last_room_fled is False
    assert len(state.discard_pile) == 0

def test_total_slain_count_logic():
    """
    Prüft, ob die Property korrekt die Anzahl der besiegten Monster zählt.
    """
    state = GameState(
        player=Player(),
        deck=Deck(),
        room=Room(),
        slain_monsters=[
            Monster(suit=Suit.SPADES, rank=10, name="Monster 1"),
            Monster(suit=Suit.CLUBS, rank=5, name="Monster 2")
        ]
    )
    
    # Die Property muss 2 zurückgeben
    assert state.total_slain_count == 2

def test_gamestate_fleeing_flag():
    """
    Stellt sicher, dass der Status des Fliehens korrekt gesetzt und gehalten wird.
    """
    state = GameState(player=Player(), deck=Deck(), room=Room())
    assert state.last_room_fled is False
    
    state.last_room_fled = True
    assert state.last_room_fled is True

# --- Integration & Persistence Tests ---

def test_gamestate_full_serialization():
    """
    Prüft, ob ein kompletter Spielzustand in ein Dictionary umgewandelt werden kann.
    Das ist wichtig für Savegames.
    """
    monster = Monster(suit=Suit.SPADES, rank=14, name="Dragon")
    state = GameState(
        player=Player(current_life=15),
        deck=Deck(cards=[monster]),
        room=Room(cards=[]),
        discard_pile=[monster]
    )
    
    data = state.model_dump()
    
    assert data["player"]["current_life"] == 15
    assert len(data["deck"]["cards"]) == 1
    assert data["discard_pile"][0]["type"] == "monster"
    assert data["discard_pile"][0]["rank"] == 14

def test_gamestate_complex_deserialization():
    """
    Testet, ob ein komplexer Zustand (mit verschiedenen Kartentypen) 
    korrekt aus einem Dictionary wiederhergestellt wird.
    """
    data = {
        "player": {"current_life": 10},
        "deck": {"cards": []},
        "room": {
            "cards": [
                {"suit": "HEARTS", "rank": 5, "name": "Potion", "type": "potion"}
            ]
        },
        "slain_monsters": [
            {"suit": "SPADES", "rank": 10, "name": "Orc", "type": "monster"}
        ]
    }
    
    state = GameState(**data)
    
    assert state.player.current_life == 10
    assert state.total_slain_count == 1
    # Prüfen, ob die Karte im Raum wirklich eine Potion-Instanz ist
    from scoundrel.models import Potion
    assert isinstance(state.room.cards[0], Potion)