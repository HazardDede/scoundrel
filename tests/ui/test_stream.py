import os

from streamlit.testing.v1 import AppTest


APP_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../scoundrel/ui/stream.py'))


def test_game_initialization():
    """Test that the app starts with a full health player."""
    at = AppTest.from_file(APP_FILE).run()

    # Check if the title is correct
    assert at.title[0].value == "🃏 Scoundrel"

    # Check if health starts at 20
    for m in at.metric:
        print(m.label)
    hp_display = next(m for m in at.metric if m.label.endswith("Lebenspunkte"))
    assert hp_display.value == "20 / 20"
