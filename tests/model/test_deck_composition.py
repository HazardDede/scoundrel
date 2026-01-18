from scoundrel.models import DeckComposition


def test_deck_composition_total_calculation():
    """Checks if the total property correctly sums up all card types."""
    comp = DeckComposition(monsters=10, potions=5, weapons=5)
    assert comp.total == 20