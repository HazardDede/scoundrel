"""
UI storage container components.
"""

from pydantic import BaseModel, ConfigDict

from scoundrel.engines.rules import RulesEngine
from scoundrel.models import GameState
from scoundrel.builders import DeckBuilder
from scoundrel.localization.base import TranslationRegistry, Translator


class AppConfig(BaseModel):
    """Configuration container."""
    language: str | None = None
    theme: str | None = None
    flavor: str | None = None


class AppState(BaseModel):
    """State container."""
    translation_registry: TranslationRegistry
    translator: Translator
    deck_builder: DeckBuilder
    game_state: GameState
    engine: RulesEngine

    model_config = ConfigDict(arbitrary_types_allowed=True)
