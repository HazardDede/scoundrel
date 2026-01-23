"""
Scoundrel Streamlit UI.
"""

import streamlit as st

from scoundrel.ui import flow, room, models, sidebar


def initialize_session() -> None:
    """Initializes the game state and engine in the session storage."""
    if 'state' not in st.session_state:
        flow.restart_game()


def main() -> None:
    """Main entrypoint."""
    initialize_session()

    state: models.AppState = st.session_state.state
    t = state.translator

    st.set_page_config(page_title="Scoundrel", layout="wide")
    st.title(t.localize('ui.main.title'))

    # Check endgame status once per rerun
    over_score = state.engine.is_game_over(state.game_state)
    victory_score = state.engine.is_victory(state.game_state)

    sidebar.render(state)

    # --- ENDGAME SCREENS ---
    if over_score is not None:
        st.error(t.localize('ui.main.game-over', score=over_score))
        return

    if victory_score is not None:
        st.success(t.localize('ui.main.victory', score=victory_score))
        st.balloons()
        return

    if room.render(state):
        st.rerun()


if __name__ == "__main__":
    main()
