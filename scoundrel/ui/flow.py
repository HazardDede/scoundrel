"""Flow UI logic."""
import os
from pathlib import Path

import streamlit as st

from scoundrel import models
from scoundrel.builders.decks import StandardDeckBuilder
from scoundrel.engines import StandardRulesEngine
from scoundrel.localization.json import JsonRegistry
from scoundrel.ui.models import AppConfig, AppState


TRANSLATIONS_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../assets/translations'))


def restart_game(config: AppConfig | None = None) -> None:
    """Resets the game state to start a new game."""
    config = config or AppConfig()

    builder = StandardDeckBuilder(config.flavor or StandardDeckBuilder.default_flavor())
    engine = StandardRulesEngine()
    registry = JsonRegistry(Path(TRANSLATIONS_PATH))
    translator = registry.get_translator(config.language or registry.default_locale, config.theme)

    state = models.GameState(
        player=models.Player(),
        deck=builder.build(shuffle=True),
        room=models.Room(),
    )
    engine.handle_next_room(state)

    st.session_state.state = AppState(
        translation_registry=registry,
        translator=translator,
        deck_builder=builder,
        game_state=state,
        engine=engine
    )
