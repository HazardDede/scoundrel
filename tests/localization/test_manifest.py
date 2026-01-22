import pytest
from pathlib import Path
from unittest.mock import MagicMock
from scoundrel.localization.manifest import TranslationManifest


@pytest.fixture
def manifest_file(tmp_path):
    # Erstellt ein temporäres Manifest mit 3 Keys
    path = tmp_path / "manifest.txt"
    content = "ui.health\nui.restart\ngame.monster_name\n# Kommentar\n"
    path.write_text(content, encoding="utf-8")
    return path


@pytest.fixture
def mock_registry():
    # Mockt die Registry, um Locales und Themes zu simulieren
    registry = MagicMock()
    registry.list_supported_locales.return_value = ["de-DE"]
    registry.list_supported_themes.return_value = ["fantasy"]

    # Mock Translators für Core und Theme
    core_translator = MagicMock()
    # Core unterstützt alles außer monster_name
    core_translator.supports.side_effect = lambda k: k != "game.monster_name"

    theme_translator = MagicMock()
    # Theme (Fantasy) unterstützt alles
    theme_translator.supports.return_value = True

    registry.get_translator.side_effect = lambda loc, theme: \
        theme_translator if theme == "fantasy" else core_translator

    return registry


def test_from_file_loading(manifest_file):
    manifest = TranslationManifest.from_file(manifest_file)
    assert len(manifest.required_keys) == 3
    assert "ui.health" in manifest.required_keys
    assert "# Kommentar" not in manifest.required_keys


def test_audit_translator(manifest_file):
    manifest = TranslationManifest.from_file(manifest_file)
    translator = MagicMock()
    # Simuliere: ui.health fehlt
    translator.supports.side_effect = lambda k: k != "ui.health"

    missing = manifest.audit_translator(translator)
    assert missing == ["ui.health"]


def test_audit_registry_structure(manifest_file, mock_registry):
    manifest = TranslationManifest.from_file(manifest_file)
    results = manifest.audit_registry(mock_registry)

    # Es sollten zwei Einträge sein: (de-DE, None) und (de-DE, 'fantasy')
    assert len(results) == 2
    assert ("de-DE", None) in results
    assert ("de-DE", "fantasy") in results

    # Im Core (None) fehlt game.monster_name (laut Mock oben)
    assert "game.monster_name" in results[("de-DE", None)]
    # Im Fantasy Theme ist alles vorhanden
    assert results[("de-DE", "fantasy")] == []
