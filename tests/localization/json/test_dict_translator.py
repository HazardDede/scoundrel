import pytest
from scoundrel.localization.json import DictTranslator


@pytest.fixture
def translation_data():
    return {
        "ui": {
            "button": {
                "restart": "Spiel neu starten",
                "welcome": "Hallo {name}!"
            }
        },
        "game": {
            "stats": "HP: {hp}/{max_hp}"
        },
        "invalid": {
            "nested": {"thing": "I am not a string directly"}
        }
    }


@pytest.fixture
def translator(translation_data):
    return DictTranslator(data=translation_data, locale="de-DE")


def test_localize_simple_key(translator):
    # Testet einfachen Zugriff und Punkt-Notation
    assert translator.localize("ui.button.restart") == "Spiel neu starten"


def test_localize_with_interpolation(translator):
    # Testet String-Formatierung mit verschiedenen Typen
    result = translator.localize("ui.button.welcome", name="Alistair")
    assert result == "Hallo Alistair!"

    # Testet numerische Werte
    stats = translator.localize("game.stats", hp=10, max_hp=20)
    assert stats == "HP: 10/20"


def test_localize_missing_key(translator):
    # Erwartetes Verhalten bei fehlendem Key
    assert translator.localize("non.existent.key") == "[non.existent.key]"


def test_localize_not_a_string(translator):
    # Wenn der Pfad auf ein Dict zeigt, sollte None/Fallback kommen
    assert translator.localize("ui.button") == "[ui.button]"


def test_supports_method(translator):
    assert translator.supports("ui.button.restart") is True
    assert translator.supports("ui.completely.wrong") is False


def test_locale_code_property(translator):
    assert translator.locale_code == "de-DE"
