"""
JSON-based localization implementation.

This module provides concrete implementations of the localization interfaces
using the local file system and JSON files as the data source.

Directory Structure Requirement:
    base_path/
    ├── core/
    │   ├── en-US.json
    │   └── de-DE.json
    └── themes/
        ├── fantasy/
        │   ├── en-US.json
        │   └── de-DE.json
        └── pirate/
            └── en-US.json

The 'core' directory defines available languages, while 'themes' contains
subdirectories that provide specific overrides for those languages.
"""
import json
from pathlib import Path
from typing import Any

from .base import Translator, TranslationRegistry


class DictTranslator(Translator):
    """
    A concrete implementation of the Translator interface that uses a dictionary
    as its data source. Supports nested keys via dot notation.
    """
    def __init__(self, data: dict[str, Any], locale: str):
        """
        Initializes the translator with translation data and a locale code.

        Args:
            data: A nested dictionary containing translation keys and values.
            locale: The language code representing this translator (e.g., 'en-US').
        """
        self._data = data
        self._locale = str(locale)

    def _lookup(self, key) -> str | None:
        """
        Internal helper to resolve a dot-notation key within the nested data structure.

        Args:
            key: The translation key (e.g., 'ui.buttons.save').

        Returns:
            The translation string if found and is a string, otherwise None.
        """
        keys = str(key).split('.')
        value = self._data
        try:
            for k in keys:
                value = value[k]

            if not isinstance(value, str):
                return None
            return value
        except (KeyError, TypeError):
            return None

    def localize(self, translation_key: str, **kwargs: str | int | float) -> str:
        value = self._lookup(translation_key)
        if not value:
            return f"[{translation_key}]"

        try:
            return value.format(**kwargs)
        except KeyError:
            return f"[{translation_key}]"

    def supports(self, translation_key: str) -> bool:
        value = self._lookup(translation_key)
        return value is not None

    @property
    def locale_code(self) -> str:
        return self._locale


class JsonRegistry(TranslationRegistry):
    """
    A JSON-based implementation of the TranslationRegistry.

    This registry manages translations stored in a specific directory structure:
    - A 'core' folder for base language strings.
    - A 'themes' folder for thematic overrides.
    """

    CONST_LOCALE_DEFAULT = "de-DE"

    def __init__(self, base_path: Path):
        """
        Initializes the registry and sets up paths for core and theme data.

        Args:
            base_path: The root directory containing 'core' and 'themes' subdirectories.
        """
        self.base_path = Path(base_path)
        self.core_path = self.base_path / "core"
        self.themes_path = self.base_path / "themes"

    @property
    def default_locale(self) -> str:
        return self.CONST_LOCALE_DEFAULT

    def list_supported_locales(self) -> list[str]:
        return sorted([f.stem for f in self.core_path.glob("*.json")])

    def list_supported_themes(self, locale: str) -> list[str]:
        if not self.themes_path.exists():
            return []
        themes = []
        for theme_dir in self.themes_path.iterdir():
            if theme_dir.is_dir() and (theme_dir / f"{locale}.json").exists():
                themes.append(theme_dir.name)
        return sorted(themes)

    def get_translator(self, locale: str, theme: str | None = None) -> DictTranslator:
        # 1. Load Core Data
        core_file = self.core_path / f"{locale}.json"
        if not core_file.exists():
            raise FileNotFoundError(f"Core locale '{locale}' not found.")

        with open(core_file, "r", encoding="utf-8") as f:
            combined_data = json.load(f)

        # 2. Layer Theme Data if provided
        if not theme:
            return DictTranslator(combined_data, locale)

        theme_file = self.themes_path / theme / f"{locale}.json"
        if theme_file.exists():
            with open(theme_file, "r", encoding="utf-8") as f:
                theme_data = json.load(f)
                self._deep_update(combined_data, theme_data)

        return DictTranslator(combined_data, locale)

    def _deep_update(self, base_dict: dict, update_dict: dict):
        """
        Recursively updates a nested dictionary.

        Unlike a standard dict.update(), this method ensures that nested
        dictionaries are merged rather than overwritten.

        Args:
            base_dict: The dictionary to be updated in-place.
            update_dict: The dictionary containing override values.
        """
        for key, value in update_dict.items():
            if isinstance(value, dict) and key in base_dict and isinstance(base_dict[key], dict):
                self._deep_update(base_dict[key], value)
            else:
                base_dict[key] = value
