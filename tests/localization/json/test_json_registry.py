import json

import pytest

from scoundrel.localization.json import JsonRegistry


@pytest.fixture
def temp_translation_dir(tmp_path):
    # Setup temporary directory structure for testing
    core_dir = tmp_path / "core"
    themes_dir = tmp_path / "themes"
    core_dir.mkdir()
    themes_dir.mkdir()

    # Create core files
    de_core = {"ui": {"start": "Start", "exit": "Ende"}}
    en_core = {"ui": {"start": "Start", "exit": "Exit"}}

    (core_dir / "de-DE.json").write_text(json.dumps(de_core), encoding="utf-8")
    (core_dir / "en-US.json").write_text(json.dumps(en_core), encoding="utf-8")

    # Create a theme (Fantasy) available in both languages
    fantasy_dir = themes_dir / "fantasy"
    fantasy_dir.mkdir()
    (fantasy_dir / "de-DE.json").write_text(json.dumps({"ui": {"start": "Abenteuer beginnen"}}))
    (fantasy_dir / "en-US.json").write_text(json.dumps({"ui": {"start": "Begin Adventure"}}))

    # Create a theme (Space) available ONLY in English
    space_dir = themes_dir / "space"
    space_dir.mkdir()
    (space_dir / "en-US.json").write_text(json.dumps({"ui": {"start": "Lift off"}}))

    return tmp_path


@pytest.fixture
def registry(temp_translation_dir):
    return JsonRegistry(temp_translation_dir)


def test_list_supported_locales(registry):
    # Prüft, ob de-DE und en-US erkannt werden
    locales = registry.list_supported_locales()
    assert locales == ["de-DE", "en-US"]


def test_list_supported_themes_filter_by_language(registry):
    # Fantasy existiert für Deutsch
    assert "fantasy" in registry.list_supported_themes("de-DE")
    # Space existiert NICHT für Deutsch
    assert "space" not in registry.list_supported_themes("de-DE")
    # Beide existieren für Englisch
    assert len(registry.list_supported_themes("en-US")) == 2


def test_get_translator_without_theme(registry):
    translator = registry.get_translator("de-DE")
    assert translator.localize("ui.start") == "Start"
    assert translator.locale_code == "de-DE"


def test_get_translator_with_theme_merging(registry):
    # Fantasy überschreibt 'ui.start', lässt 'ui.exit' aber unberührt
    translator = registry.get_translator("de-DE", theme="fantasy")

    assert translator.localize("ui.start") == "Abenteuer beginnen"
    assert translator.localize("ui.exit") == "Ende"


def test_get_translator_raises_file_not_found(registry):
    with pytest.raises(FileNotFoundError):
        registry.get_translator("fr-FR")


def test_deep_update_logic(registry):
    # Manueller Test der rekursiven Update-Logik
    base = {"a": {"b": 1, "c": 2}, "d": 4}
    update = {"a": {"b": 99}, "e": 5}

    registry._deep_update(base, update)

    assert base["a"]["b"] == 99
    assert base["a"]["c"] == 2  # c muss erhalten bleiben!
    assert base["d"] == 4
    assert base["e"] == 5
