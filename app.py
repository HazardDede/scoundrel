import streamlit as st
import functools
from scoundrel.builders import BeginnerDeckBuilder
from scoundrel.engine import StandardRulesEngine
from scoundrel import models


# --- STATE INIT ---

if 'state' not in st.session_state:
    builder = BeginnerDeckBuilder()
    engine = StandardRulesEngine()
    
    # Initialize a fresh game state
    state = models.GameState(
        player=models.Player(),
        deck=builder.build_deck(shuffle=True),
        room=models.Room(),
    )
    # Fill the first room immediately
    engine.handle_next_room(state)
    
    st.session_state.state = state
    st.session_state.engine = engine

state = st.session_state.state
engine = st.session_state.engine


# --- UTILITY ---

def check_room_transition():
    """Automatically refills the room if 0 or 1 card is left."""
    # English comment: Rule check: Refill room if it's depleted
    if engine.next_room_available(state):
        engine.handle_next_room(state)


# --- STATUS CHECKS ---

is_dead = state.player.is_dead
is_victory = state.deck.remaining == 0 and state.room.remaining == 0
game_active = not is_dead and not is_victory


# --- UI LAYOUT ---

st.set_page_config(page_title="Scoundrel", layout="wide")
st.title("🃏 Scoundrel")


# --- SIDEBAR: STATS & WEAPON ---
with st.sidebar:
    st.header("Held")
    st.metric("Lebenspunkte", f"{state.player.current_life} / {state.player.max_life}")
    
    st.divider()
    st.header("Ausrüstung")
    if state.player.has_weapon:
        weapon = state.player.weapon
        st.success(f"🗡️ **{weapon.weapon.name}**\n\nStärke: {weapon.weapon.protection}")
        
        # English comment: Display the rank of the last monster defeated with this weapon
        if weapon.slain_monsters:
            last_monster = weapon.slain_monsters[-1]
            st.warning(f"Zuletzt besiegt: {last_monster.name} (Rang {last_monster.rank})")
            st.caption(f"Effektiv gegen Monster < {last_monster.rank}")
        else:
            st.info("Waffe ist unbenutzt.")
    else:
        st.write("Keine Waffe.")

    st.divider()
    if st.button("🔄 Spiel neu starten", use_container_width=True):
        del st.session_state.state
        st.rerun()

# --- HAUPTFELD: DER RAUM ---
if is_dead:
    st.error("💀 GAME OVER - Du bist im Dungeon gestorben.")
elif is_victory:
    st.success("🏆 SIEG - Du hast den Dungeon lebend verlassen!")
    st.balloons()
else:
    st.subheader(f"Aktueller Raum ({state.deck.remaining} Karten im Deck)")

# Anzeige der 4 Karten-Slots
cols = st.columns(4)

for i, card in enumerate(state.room.cards):
    with cols[i]:
        # Visualisierung basierend auf Kartentyp
        if isinstance(card, models.Monster):
            st.error(f"👹 **{card.name}**")
            
            # Bare-Hand Attack
            p_fists = engine.preview_attack(state, card, False)
            if st.button(f"Fäuste (-{p_fists.damage_taken} HP)", key=f"fist_{i}", disabled=not game_active):
                engine.handle_monster_attack(state, card, False)
                check_room_transition()
                st.rerun()
            
            # Weapon Attack
            can_use_weapon = engine.can_attack_monster(state, card, True)
            if can_use_weapon:
                p_weapon = engine.preview_attack(state, card, True)
                if st.button(f"Waffe (-{p_weapon.damage_taken} HP)", key=f"weapon_{i}", disabled=not game_active):
                    engine.handle_monster_attack(state, card, True)
                    check_room_transition()
                    st.rerun()
            else:
                st.button("Waffe blockiert", key=f"weapon_dis_{i}", disabled=True)

        elif isinstance(card, models.Potion):
            st.success(f"🧪 **{card.name}**")
            if engine.can_drink_potion(state, card):
                p_heal = engine.preview_potion(state, card)
                if st.button(f"Trinken (+{p_heal.healing_received} HP)", key=f"pot_{i}", disabled=not game_active):
                    engine.handle_drink_potion(state, card)
                    check_room_transition()
                    st.rerun()
            else:
                st.button("Schon getrunken", key=f"pot_dis_{i}", disabled=True)

        elif isinstance(card, models.Weapon):
            st.warning(f"⚔️ **{card.name}**")
            if st.button("Ausrüsten", key=f"equip_{i}", disabled=not game_active):
                engine.handle_equip_weapon(state, card)
                check_room_transition()
                st.rerun()


# --- RAUM-AKTIONEN ---

st.divider()

if engine.can_flee_room(state):
    if st.button("🏃 In den nächsten Raum fliehen", use_container_width=True, disabled=not game_active):
        engine.handle_flee_room(state)
        engine.handle_next_room(state)
        st.rerun()
else:
    # Information warum Flucht nicht möglich ist
    flee_reason = "Raum nicht voll" if len(state.room.cards) < 4 else "Letzten Raum geflohen"
    if game_active:
        st.button(f"Fliehen nicht möglich ({flee_reason})", disabled=True, use_container_width=True)

# Footer Info
st.caption("Regeln: Du kannst fliehen, wenn der Raum unangetastet ist und du nicht im letzten Raum geflohen bist.")
st.caption("Ein Raum wird automatisch aufgefüllt, wenn 0 oder 1 Karte übrig ist.")