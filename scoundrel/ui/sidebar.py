"""Sidebar UI component."""
import streamlit as st

from scoundrel.ui import flow
from scoundrel.ui.models import AppConfig, AppState


def render(state: AppState) -> None:
    """Renders player stats and equipment info in the sidebar."""
    t = state.translator

    with st.sidebar:
        with st.expander(t.localize('ui.sidebar.settings.label')):
            language_options = state.translation_registry.list_supported_locales()
            language_current = t.locale_code
            try:
                default_lang_index = language_options.index(language_current)
            except ValueError:
                default_lang_index = 0

            language_selector = st.selectbox(
                label=t.localize('ui.sidebar.settings.selector-language.label'),
                options=language_options,
                index=default_lang_index,
                key="language_selector"
            )

            theme_options = ['core'] + state.translation_registry.list_supported_themes(language_selector)
            theme_current = t.theme or 'core'

            try:
                default_theme_index = theme_options.index(theme_current)
            except ValueError:
                default_theme_index = 0

            theme_selector = st.selectbox(
                label=t.localize('ui.sidebar.settings.selector-theme.label'),
                options=theme_options,
                index=default_theme_index,
                key="theme_selector"
            )

            flavor_options = state.deck_builder.supported_flavors()
            flavor_current = state.deck_builder.flavor

            try:
                default_index = flavor_options.index(flavor_current)
            except ValueError:
                default_index = 0

            deck_flavor_selector = st.selectbox(
                label=t.localize('ui.sidebar.settings.selector-flavor.label'),
                options=flavor_options,
                index=default_index,
                key="deck_flavor_selector"
            )

            language_change = language_selector != language_current
            theme_change = theme_selector != theme_current
            flavor_change = deck_flavor_selector != flavor_current

            if language_change or theme_change or flavor_change:
                st.sidebar.warning(
                    t.localize('ui.sidebar.settings.warning-change.label')
                )

            if st.button(t.localize("ui.sidebar.settings.button-restart.label"), use_container_width=True):
                flow.restart_game(AppConfig(
                    language=language_selector, theme=theme_selector, flavor=deck_flavor_selector
                ))
                st.rerun()

        st.divider()

        st.header(t.localize('ui.sidebar.hero.label'))
        st.metric(
            t.localize('ui.sidebar.hero.health.label'),
            t.localize('ui.sidebar.hero.health.value', player=state.game_state.player)
        )

        st.header(t.localize('ui.sidebar.hero.weapon.label'))

        if state.game_state.player.has_weapon:
            equipped = state.game_state.player.equipped
            assert equipped is not None

            st.success(t.localize(
                'ui.sidebar.hero.weapon.equipped', weapon=equipped.weapon.localize(t)
            ))

            if equipped.slain_monsters:
                last_monster = equipped.slain_monsters[-1]
                st.error(t.localize(
                    'ui.sidebar.hero.weapon.last-slain',
                    monster=last_monster.localize(t),
                ))
            else:
                st.info(t.localize('ui.sidebar.hero.weapon.unused'))
        else:
            st.info(t.localize('ui.sidebar.hero.weapon.bare-handed'))
