"""
Scoundrel Streamlit frontend.
"""

import streamlit as st
from scoundrel import models
from scoundrel.builders.decks import StandardDeckBuilder, DeckFlavor
from scoundrel.themes import FantasyTheme
from scoundrel.engines import StandardRulesEngine


# --- CONFIGURATION ---

def initialize_session():
    """Initializes the game state and engine in the session storage."""
    if 'state' not in st.session_state:
        builder = StandardDeckBuilder(DeckFlavor.BEGINNER)
        engine = StandardRulesEngine()

        state = models.GameState(
            player=models.Player(),
            deck=FantasyTheme().apply_to(builder.build(shuffle=True)),
            room=models.Room(),
        )
        engine.handle_next_room(state)

        st.session_state.state = state
        st.session_state.engine = engine


def reset_game():
    """Clears the session state to start a fresh game."""
    del st.session_state.state


# --- COMPONENT RENDERING ---

def render_sidebar(state):
    """Renders player stats and equipment info in the sidebar."""
    with st.sidebar:
        st.header("Held")
        st.metric("Lebenspunkte ❤️", f"{state.player.current_life} / {state.player.max_life}")

        st.divider()
        st.header("⚔️ Ausrüstung 🛡️")

        if state.player.has_weapon:
            equipped = state.player.equipped
            st.success(f"🗡️ **{equipped.weapon.name}**\n\n⚡ {equipped.weapon.protection}")

            if equipped.slain_monsters:
                last_monster = equipped.slain_monsters[-1]
                st.warning(f"Letzter Gegner: {last_monster.name} (Rang {last_monster.strength})")
                st.caption(f"Effektiv gegen < {last_monster.strength}")
            else:
                st.info("Waffe ist unbenutzt.")
        else:
            st.write("Noch keine Waffe ausgerüstet.")

        st.divider()
        st.button("🔄 Spiel neu starten", use_container_width=True, on_click=reset_game)


def render_monster_ui(engine, state, card, idx, active):
    """Renders monster specific action buttons."""
    st.error(f"{card.emoji or '👹'} **{card.name}** (💪 {card.strength})")

    # Weapon Attack
    if engine.can_attack_monster(state, card, True):
        p_weapon = engine.preview_attack(state, card, True)
        if st.button(f"Waffe (-{p_weapon.damage_taken} LP)", key=f"weapon_{idx}", disabled=not active):
            engine.handle_monster_attack(state, card, True)
            return True
    else:
        txt = "Waffe ineffektiv" if state.player.has_weapon else "Keine Waffe"
        st.button(txt, key=f"weapon_dis_{idx}", disabled=True)

    # Bare-Hand Attack
    p_fists = engine.preview_attack(state, card, False)
    if st.button(f"Fäuste (-{p_fists.damage_taken} LP)", key=f"fist_{idx}", disabled=not active):
        engine.handle_monster_attack(state, card, False)
        return True

    return False


def render_potion_ui(engine, state, card, idx, active):
    """Renders potion specific action buttons."""
    st.success(f"{card.emoji or '🧪'} **{card.name}** (❤️ +{card.potency})")
    if engine.can_drink_potion(state, card):
        p_heal = engine.preview_potion(state, card)
        if st.button(f"Trinken (+{p_heal.healing_received} LP)", key=f"pot_{idx}", disabled=not active):
            engine.handle_drink_potion(state, card)
            return True
    else:
        st.button("Nicht möglich", key=f"pot_dis_{idx}", disabled=True)
    return False


def render_weapon_ui(engine, state, card, idx, active):
    """Renders weapon specific action buttons."""
    st.warning(f"{card.emoji or '⚔'}️ **{card.name}** (🛡️ {card.protection})")
    if st.button("Ausrüsten", key=f"equip_{idx}", disabled=not active):
        engine.handle_equip_weapon(state, card)
        return True
    return False


# --- MAIN APP LOGIC ---

def main():
    """Main entrypoint."""
    st.set_page_config(page_title="Scoundrel", layout="wide")
    st.title("🃏 Scoundrel")

    initialize_session()
    state = st.session_state.state
    engine = st.session_state.engine

    # Check endgame status once per rerun
    over_score = engine.is_game_over(state)
    victory_score = engine.is_victory(state)
    game_active = over_score is None and victory_score is None

    render_sidebar(state)

    # --- ENDGAME SCREENS ---
    if over_score is not None:
        st.error(f"💀 GAME OVER\nDein Highscore: {over_score}")
        return

    if victory_score is not None:
        st.success(f"🏆 SIEG! - Du hast den Dungeon überlebt!\nHighscore: {victory_score}")
        st.balloons()
        return

    # --- ROOM RENDERING ---
    st.subheader(f"Aktueller Raum ({state.deck.remaining} Karten im Deck)")
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
        if st.button("🏃 In den nächsten Raum fliehen", use_container_width=True, disabled=not game_active):
            engine.handle_flee_room(state)
            engine.handle_next_room(state)
            st.rerun()
    else:
        reason = "Raum schon begonnen" if len(state.room.cards) < 4 else "Aus dem letzten Raum geflohen"
        st.button(f"Fliehen nicht möglich ({reason})", disabled=True, use_container_width=True)


if __name__ == "__main__":
    main()
