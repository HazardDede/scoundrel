"""
Scoundrel Streamlit frontend.
"""
import os.path
from pathlib import Path

import streamlit as st

from scoundrel import models
from scoundrel.builders.decks import StandardDeckBuilder
from scoundrel.engines import StandardRulesEngine
from scoundrel.localization.json import JsonRegistry

TRANSLATIONS_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../assets/translations'))


# --- CONFIGURATION ---

def restart_game(flavor: str | None = None):
    """Resets the game state to start a new game."""
    builder = StandardDeckBuilder(flavor or StandardDeckBuilder.default_flavor())
    engine = StandardRulesEngine()
    registry = JsonRegistry(Path(TRANSLATIONS_PATH))
    translator = registry.get_translator('de-DE', 'fantasy')

    state = models.GameState(
        player=models.Player(),
        deck=builder.build(shuffle=True),
        room=models.Room(),
    )
    engine.handle_next_room(state)

    st.session_state.translation_registry = registry
    st.session_state.translator = translator
    st.session_state.builder = builder
    st.session_state.state = state
    st.session_state.engine = engine


def initialize_session():
    """Initializes the game state and engine in the session storage."""
    if 'state' not in st.session_state:
        restart_game()


# --- COMPONENT RENDERING ---

def render_sidebar(state):
    """Renders player stats and equipment info in the sidebar."""
    t = st.session_state.translator

    with st.sidebar:
        with st.expander(t.localize('ui.sidebar.settings.label')):
            flavor_options = st.session_state.builder.supported_flavors()
            flavor_current = st.session_state.builder.flavor.value

            try:
                default_index = flavor_options.index(flavor_current)
            except ValueError:
                default_index = 0

            deck_flavor_selector = st.selectbox(
                label=t.localize('ui.sidebar.settings.selector_flavor.label'),
                options=flavor_options,
                index=default_index,
                key="deck_flavor_selector"
            )

            if deck_flavor_selector != flavor_current:
                st.sidebar.warning(
                    t.localize('ui.sidebar.settings.warning_change.label')
                )

            if st.button(t.localize("ui.sidebar.settings.button_restart.label"), use_container_width=True):
                restart_game(deck_flavor_selector)
                st.rerun()

        st.divider()

        st.header(t.localize('ui.sidebar.hero.label'))
        st.metric(
            t.localize('ui.sidebar.hero.health.label'),
            t.localize('ui.sidebar.hero.health.value', player=state.player)
        )

        st.header(t.localize('ui.sidebar.hero.weapon.label'))

        if state.player.has_weapon:
            equipped = state.player.equipped

            st.success(t.localize(
                'ui.sidebar.hero.weapon.equipped', weapon=equipped.weapon.localize(t)
            ))

            if equipped.slain_monsters:
                last_monster = equipped.slain_monsters[-1]
                st.error(t.localize(
                    'ui.sidebar.hero.weapon.last_slain',
                    monster=last_monster.localize(t),
                ))
            else:
                st.info(t.localize('ui.sidebar.hero.weapon.unused'))
        else:
            st.info(t.localize('ui.sidebar.hero.weapon.bare-handed'))


def render_monster_ui(engine, state, card, idx, active):
    """Renders monster specific action buttons."""
    t = st.session_state.translator

    st.error(t.localize('ui.main.room.monster.card', card=card.localize(t)))

    # Weapon Attack
    if engine.can_attack_monster(state, card, True):
        p_weapon = engine.preview_attack(state, card, True)
        if st.button(
                t.localize('ui.main.room.button-attack-weapon.ok', preview=p_weapon),
                key=f"weapon_{idx}", disabled=not active
        ):
            engine.handle_monster_attack(state, card, True)
            return True
    else:
        txt = (
            t.localize('ui.main.room.button-attack-weapon.ineffective')
            if state.player.has_weapon
            else t.localize('ui.main.room.button-attack-weapon.no')
        )
        st.button(txt, key=f"weapon_dis_{idx}", disabled=True)

    # Bare-Hand Attack
    p_fists = engine.preview_attack(state, card, False)
    if st.button(
            t.localize('ui.main.room.button-attack-bare-handed.label', preview=p_fists),
            key=f"fist_{idx}", disabled=not active
    ):
        engine.handle_monster_attack(state, card, False)
        return True

    return False


def render_potion_ui(engine, state, card, idx, active):
    """Renders potion specific action buttons."""
    t = st.session_state.translator

    st.success(t.localize('ui.main.room.potion.card', card=card.localize(t)))
    if engine.can_drink_potion(state, card):
        p_heal = engine.preview_potion(state, card)
        if st.button(
            t.localize('ui.main.room.button-drink-potion.ok', preview=p_heal),
            key=f"pot_{idx}", disabled=not active
        ):
            engine.handle_drink_potion(state, card)
            return True
    else:
        st.button(t.localize('ui.main.room.button-drink-potion.no'), key=f"pot_dis_{idx}", disabled=True)

    return False


def render_weapon_ui(engine, state, card, idx, active):
    """Renders weapon specific action buttons."""
    t = st.session_state.translator

    st.warning(t.localize('ui.main.room.weapon.card', card=card.localize(t)))
    if st.button(t.localize('ui.main.room.button-equip-weapon.ok'), key=f"equip_{idx}", disabled=not active):
        engine.handle_equip_weapon(state, card)
        return True
    return False


# --- MAIN APP LOGIC ---

def main():
    """Main entrypoint."""
    initialize_session()
    state = st.session_state.state
    engine = st.session_state.engine
    t = st.session_state.translator

    st.set_page_config(page_title="Scoundrel", layout="wide")
    st.title(t.localize('ui.main.title'))

    # Check endgame status once per rerun
    over_score = engine.is_game_over(state)
    victory_score = engine.is_victory(state)
    game_active = over_score is None and victory_score is None

    render_sidebar(state)

    # --- ENDGAME SCREENS ---
    if over_score is not None:
        st.error(t.localize('ui.main.game-over', score=over_score))
        return

    if victory_score is not None:
        st.success(t.localize('ui.main.victory', score=victory_score))
        st.balloons()
        return

    # --- ROOM RENDERING ---
    st.subheader(t.localize('ui.main.room.label', deck=state.deck))
    cols = st.columns(4)

    action_taken = False
    for i, card in enumerate(state.room.cards):
        with cols[i]:
            if isinstance(card, models.Monster):
                action_taken = render_monster_ui(engine, state, card, i, game_active)
            elif isinstance(card, models.Potion):
                action_taken = render_potion_ui(engine, state, card, i, game_active)
            elif isinstance(card, models.Weapon):
                action_taken = render_weapon_ui(engine, state, card, i, game_active)

            if action_taken:
                if engine.next_room_available(state):
                    engine.handle_next_room(state)
                st.rerun()

    # --- FLEE LOGIC ---
    st.divider()
    if engine.can_flee_room(state):
        if st.button(t.localize('ui.main.room.flee.ok'), use_container_width=True, disabled=not game_active):
            engine.handle_flee_room(state)
            engine.handle_next_room(state)
            st.rerun()
    else:
        txt = (
            t.localize('ui.main.room.flee.no-started')
            if len(state.room.cards) < 4
            else t.localize('ui.main.room.flee.no-last-fleed')
        )
        st.button(txt, disabled=True, use_container_width=True)


if __name__ == "__main__":
    main()
