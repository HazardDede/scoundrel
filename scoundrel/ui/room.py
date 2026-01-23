"""Room UI component."""
import streamlit as st

from scoundrel.engines import RulesEngine
from scoundrel import models
from scoundrel.ui.models import AppState


def _render_monster_ui(engine: RulesEngine, state: AppState, card: models.Monster, idx: int) -> bool:
    """Renders monster specific action buttons."""
    t = state.translator

    st.error(t.localize('ui.main.room.monster.card', card=card.localize(t)))

    # Weapon Attack
    if engine.can_attack_monster(state.game_state, card, True):
        p_weapon = engine.preview_attack(state.game_state, card, True)
        if st.button(
                t.localize('ui.main.room.button-attack-weapon.ok', preview=p_weapon),
                key=f"weapon_{idx}"
        ):
            engine.handle_monster_attack(state.game_state, card, True)
            return True
    else:
        txt = (
            t.localize('ui.main.room.button-attack-weapon.ineffective')
            if state.game_state.player.has_weapon
            else t.localize('ui.main.room.button-attack-weapon.no')
        )
        st.button(txt, key=f"weapon_dis_{idx}", disabled=True)

    # Bare-Hand Attack
    p_fists = engine.preview_attack(state.game_state, card, False)
    if st.button(
            t.localize('ui.main.room.button-attack-bare-handed.label', preview=p_fists),
            key=f"fist_{idx}"
    ):
        engine.handle_monster_attack(state.game_state, card, False)
        return True

    return False


def _render_potion_ui(engine: RulesEngine, state: AppState, card: models.Potion, idx: int) -> bool:
    """Renders potion specific action buttons."""
    t = state.translator

    st.success(t.localize('ui.main.room.potion.card', card=card.localize(t)))
    if engine.can_drink_potion(state.game_state, card):
        p_heal = engine.preview_potion(state.game_state, card)
        if st.button(
            t.localize('ui.main.room.button-drink-potion.ok', preview=p_heal),
            key=f"pot_{idx}"
        ):
            engine.handle_drink_potion(state.game_state, card)
            return True
    else:
        st.button(t.localize('ui.main.room.button-drink-potion.no'), key=f"pot_dis_{idx}", disabled=True)

    return False


def _render_weapon_ui(engine: RulesEngine, state: AppState, card: models.Weapon, idx: int) -> bool:
    """Renders weapon specific action buttons."""
    t = state.translator

    st.warning(t.localize('ui.main.room.weapon.card', card=card.localize(t)))
    if st.button(t.localize('ui.main.room.button-equip-weapon.ok'), key=f"equip_{idx}"):
        engine.handle_equip_weapon(state.game_state, card)
        return True
    return False


def render(state: AppState) -> bool:
    """Renders the room """
    t = state.translator

    st.subheader(t.localize('ui.main.room.label', deck=state.game_state.deck))
    cols = st.columns(4)
    action_taken = False

    for i, card in enumerate(state.game_state.room.cards):
        with cols[i]:
            if isinstance(card, models.Monster):
                action_taken = _render_monster_ui(state.engine, state, card, i)
            elif isinstance(card, models.Potion):
                action_taken = _render_potion_ui(state.engine, state, card, i)
            elif isinstance(card, models.Weapon):
                action_taken = _render_weapon_ui(state.engine, state, card, i)

            if action_taken:
                if state.engine.next_room_available(state.game_state):
                    state.engine.handle_next_room(state.game_state)
                return True

    # --- FLEE LOGIC ---
    st.divider()
    if state.engine.can_flee_room(state.game_state):
        if st.button(t.localize('ui.main.room.flee.ok'), use_container_width=True):
            state.engine.handle_flee_room(state.game_state)
            state.engine.handle_next_room(state.game_state)
            return True
    else:
        txt = (
            t.localize('ui.main.room.flee.no-started')
            if len(state.game_state.room.cards) < 4
            else t.localize('ui.main.room.flee.no-last-fleed')
        )
        st.button(txt, disabled=True, use_container_width=True)

    return False
