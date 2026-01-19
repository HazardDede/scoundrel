import pytest

from scoundrel.builders import DeckFlavor
from scoundrel.builders import StandardDeckBuilder
from scoundrel.models import Monster, Potion, Weapon


@pytest.fixture
def builder():
    return StandardDeckBuilder()


# --- Structural Tests ---

def test_standard_builder_total_count(builder):
    """Verifies the standard deck contains exactly 44 cards."""
    deck = builder.build(shuffle=False)
    assert deck.remaining == 44


@pytest.mark.parametrize("flavor, expected_total, monsters, potions, weapons", [
    (DeckFlavor.Beginner, 52, 26, 13, 13),
    (DeckFlavor.Quick, 22, 14, 4, 4),
    (DeckFlavor.Standard, 44, 26, 9, 9),
])
def test_standard_builder_composition_stats(flavor, expected_total, monsters, potions, weapons):
    """Uses the deck's own composition property to verify card types."""
    deck = StandardDeckBuilder(flavor=flavor).build(shuffle=False)
    comp = deck.composition
    
    assert comp.monsters == monsters
    assert comp.potions == potions
    assert comp.weapons == weapons
    assert comp.total == expected_total


def test_standard_builder_rank_ranges(builder):
    """Checks if the ranks for each card type are within the expected Scoundrel limits."""
    deck = builder.build(shuffle=False)
    
    monsters = [c for c in deck.cards if isinstance(c, Monster)]
    potions = [c for c in deck.cards if isinstance(c, Potion)]
    weapons = [c for c in deck.cards if isinstance(c, Weapon)]
    
    # Monsters should be 2 to 14 (Ace)
    assert min(m.rank for m in monsters) == 2
    assert max(m.rank for m in monsters) == 14
    
    # Potions and Weapons should be 2 to 10 (Aces removed)
    assert max(p.rank for p in potions) == 10
    assert max(w.rank for w in weapons) == 10


# --- Behavior Tests ---

def test_standard_builder_shuffling_logic(builder):
    """Ensures that shuffle=True actually changes the order of cards."""
    # We create two decks. Note: There's a near-zero chance they are identical.
    deck_ordered = builder.build(shuffle=False)
    deck_shuffled = builder.build(shuffle=True)
    
    ordered_ids = [c.card_id for c in deck_ordered.cards]
    shuffled_ids = [c.card_id for c in deck_shuffled.cards]
    
    assert ordered_ids != shuffled_ids
    assert len(shuffled_ids) == 44  # Integrity must remain


def test_standard_builder_id_uniqueness(builder):
    """Ensures every card in the generated deck has a unique card_id."""
    deck = builder.build()
    ids = [c.card_id for c in deck.cards]
    
    # Using a set to find duplicates
    assert len(ids) == len(set(ids)), "Duplicate card IDs found in deck!"


# --- Edge Cases ---

def test_standard_builder_deterministic_without_shuffle(builder):
    """Ensures that without shuffling, the builder always produces the same order."""
    deck_1 = builder.build(shuffle=False)
    deck_2 = builder.build(shuffle=False)
    
    ids_1 = [c.card_id for c in deck_1.cards]
    ids_2 = [c.card_id for c in deck_2.cards]
    
    assert ids_1 == ids_2
