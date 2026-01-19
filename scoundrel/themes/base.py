from abc import ABC, abstractmethod
from copy import deepcopy

from pydantic import BaseModel

from scoundrel.models import Deck, Suit, Rank


class Theme(ABC):
    def apply_to(self, deck: Deck) -> Deck:
        themed_deck = self._apply_to(deepcopy(deck))

        if deck.remaining != themed_deck.remaining:
            raise RuntimeError(
                f"Theme is not supposed to change the deck: {deck.remaining} vs {themed_deck.remaining} cards"
            )

        if deck.composition != themed_deck.composition:
            raise RuntimeError(
                f"Theme is not supposed to change the deck: Composition mismatch"
            )

        return themed_deck

    @abstractmethod
    def _apply_to(self, deck: Deck) -> Deck:
        raise NotImplementedError()


class CardIdentity(BaseModel):
    name: str
    emoji: str


CardAtlas = dict[tuple[Suit, Rank], CardIdentity]


class AtlasTheme(Theme):
    def __init__(self, atlas: CardAtlas):
        self.atlas = atlas

    def _apply_to(self, deck: Deck) -> Deck:
        themed_cards = []

        for card in deck.cards:
            identity = self.atlas.get((card.suit, card.rank))
            if not identity:
                # Not found, keep as is
                themed_cards.append(card)
                continue

            # Use model_copy to create a new instance with a modified attribute
            # Remember: We cannot change in-place as the card is frozen
            new_card = card.model_copy(update={
                "name": identity.name,
                "emoji": identity.emoji
            })
            themed_cards.append(new_card)

        return Deck(cards=themed_cards)
