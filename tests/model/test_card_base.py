import pytest
from pydantic import ValidationError
from scoundrel.models import Card, Suit

# --- Initialization & Logic Tests ---

def test_card_initialization_valid():
    """
    Ensures a card is correctly initialized and all fields are accessible.
    """
    card = Card(suit=Suit.SPADES, rank=14, name="Ace of Spades", type="base")
    assert card.suit == Suit.SPADES
    assert card.rank == 14
    assert card.name == "Ace of Spades"
    assert card.type == "base"


def test_card_id_generation():
    """
    Ensures the computed card_id is correctly formatted.
    """
    card = Card(suit=Suit.CLUBS, rank=7, name="Seven of Clubs", type="base")
    assert card.card_id == "CLUBS_7"


# --- Representation Tests (str & repr) ---

def test_card_str_format():
    """
    Checks if the __str__ method provides the expected human-readable output.
    """
    card = Card(suit=Suit.HEARTS, rank=13, name="King of Hearts", type="base")
    # Assuming __str__ is implemented as: f"{self.name} ({self.card_id})"
    assert str(card) == "King of Hearts (HEARTS_13)"


def test_card_repr_contains_data():
    """
    Checks if the repr contains the class name and essential attributes.
    """
    card = Card(suit=Suit.SPADES, rank=2, name="Two of Spades", type="base")
    representation = repr(card)
    assert "Card" in representation
    assert "SPADES_2" in representation


# --- Serialization Tests ---

def test_card_to_dict_includes_computed_id():
    """
    Ensures the card_id is present when converting the model to a dictionary.
    """
    card = Card(suit=Suit.DIAMONDS, rank=9, name="Nine of Diamonds", type="base")
    data = card.model_dump()
    
    assert "card_id" in data
    assert data["card_id"] == "DIAMONDS_9"


def test_card_from_dict():
    """
    Ensures a card can be correctly reconstructed from a dictionary (JSON-like).
    """
    data = {
        "suit": "Clubs",
        "rank": 8,
        "name": "Eight of Clubs",
        "type": "base"
    }
    card = Card(**data)
    assert card.suit == Suit.CLUBS
    assert card.rank == 8
    assert card.card_id == "CLUBS_8"


# --- Error Handling & Validation ---

@pytest.mark.parametrize("invalid_rank", ["High", None, [10]])
def test_card_invalid_rank_type(invalid_rank):
    """
    Ensures that Pydantic raises an error if rank is not an integer.
    """
    with pytest.raises(ValidationError):
        Card(suit=Suit.SPADES, rank=invalid_rank, name="Invalid Card", type="base")


def test_card_invalid_suit_type():
    """
    Ensures that providing an invalid suit string raises an error.
    """
    with pytest.raises(ValidationError):
        Card(suit="JOKERS", rank=10, name="Invalid Suit", type="base")


# --- Immutable test ---

def test_card_is_immutable():
    """
    Verifies that we cannot change the rank after the card is created.
    """
    card = Card(suit=Suit.DIAMONDS, rank=10, name="Ten of Diamonds", type="base")
    
    # This block expects a ValidationError (FrozenInstanceError is a subclass of it)
    with pytest.raises(ValidationError):
        card.rank = 11  # This line MUST raise an exception now
