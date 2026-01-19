import pytest
from scoundrel import models
from scoundrel.themes import AtlasTheme, CardIdentity


# --- Successful mapping

def test_atlas_theme_mapping_success():
    # Setup a small atlas and a deck with one matching card
    atlas = {
        (models.Suit.HEARTS, 5): CardIdentity(name="Super Trank", emoji="🧪")
    }
    theme = AtlasTheme(atlas=atlas)

    card = models.Potion(suit=models.Suit.HEARTS, rank=5, name="Normaler Trank", emoji="🩹")
    deck = models.Deck(cards=[card])

    themed_deck = theme.apply_to(deck)

    # Verify the card was copied and updated correctly
    assert themed_deck.cards[0].name == "Super Trank"
    assert themed_deck.cards[0].emoji == "🧪"
    assert themed_deck.cards[0] is not deck.cards[0]  # Should be a new instance


# --- Fallback if card not in atlas

def test_atlas_theme_missing_entry():
    # English comment: Empty atlas should result in an identical deck (but new instances)
    theme = AtlasTheme(atlas={})
    card = models.Monster(suit=models.Suit.SPADES, rank=14, name="Drache", emoji="🐉")
    deck = models.Deck(cards=[card])

    themed_deck = theme.apply_to(deck)

    assert themed_deck.cards[0].name == "Drache"
    assert len(themed_deck.cards) == 1


# --- Integrity checks

class BrokenSizeTheme(AtlasTheme):
    def _apply_to(self, deck: models.Deck) -> models.Deck:
        # English comment: Illegally removing a card
        deck.cards.pop()
        return deck


class BrokenCompositionTheme(AtlasTheme):
    def _apply_to(self, deck: models.Deck) -> models.Deck:
        # English comment: Illegally changing a Potion to a Monster
        deck.cards[0] = models.Monster(suit=models.Suit.SPADES, rank=2, name="Bug")
        return deck


def test_theme_integrity_checks():
    card = models.Potion(suit=models.Suit.HEARTS, rank=2, name="Test")
    deck = models.Deck(cards=[card])

    # Check size mismatch
    with pytest.raises(RuntimeError, match="1 vs 0 cards"):
        BrokenSizeTheme(atlas={}).apply_to(deck)

    # Check composition mismatch
    with pytest.raises(RuntimeError, match="Composition mismatch"):
        BrokenCompositionTheme(atlas={}).apply_to(deck)
