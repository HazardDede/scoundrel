"""
Localization abstractions for the Scoundrel application.

This module defines the core interfaces for handling multi-language support
and thematic overrides (flavors). It follows a provider-based pattern where
a 'TranslationRegistry' acts as a factory to fetch specific 'Translator'
instances based on a combination of language and visual theme.

Architecture:
    - Translator: Responsible for resolving keys into formatted strings.
    - TranslationRegistry: Responsible for discovering and loading
      translation assets (files, DB, etc.) and managing themes.

Example:
    registry: TranslationRegistry = JsonRegistry(path)
    translator = registry.get_translator("de-DE", theme="fantasy")
    print(translator.localize("ui.welcome", name="Alistair"))
"""
from abc import ABC, abstractmethod
from typing import Any


class Translator(ABC):
    """
    Interface for resolving translation keys into localized strings.

    Implementations are responsible for one specific locale and handle
    the actual string lookup and formatting.
    """
    @abstractmethod
    def localize(self, translation_key: str, **kwargs: Any) -> str:
        """
        Retrieves and formats a localized string.

        Args:
            translation_key: A unique identifier for the string (e.g., 'ui.save').
            **kwargs: Dynamic values to be interpolated into the translation string.

        Returns:
            The formatted localized string. If the key is missing,
            a fallback (usually '[key]') should be returned.
        """

    @abstractmethod
    def supports(self, translation_key: str) -> bool:
        """
        Verifies if a specific translation key exists in this translator.

        Args:
            translation_key: The key to check.

        Returns:
            True if the key is available and can be localized, False otherwise.
        """

    @property
    @abstractmethod
    def locale_code(self) -> str:
        """
        The language code associated with this translator instance.

        Returns:
            A string representing the locale (e.g., 'en-US' or 'de-DE').
        """

    @property
    @abstractmethod
    def theme(self) -> str | None:
        """
        The theme associated with this translator instance.

        Returns:
            A string representing the theme (e.g., 'fantasy', 'sci-fi')
        """


class TranslationRegistry(ABC):
    """
    Interface for managing and providing access to multiple translators.

    The registry acts as a factory and discovery service for all available
    locales and their optional thematic variations (themes).
    """
    @abstractmethod
    def get_translator(self, locale: str, theme: str | None = None) -> Translator:
        """
        Creates or retrieves a Translator instance for a specific locale and theme.

        Args:
            locale: The requested language code.
            theme: An optional theme name to apply as an override layer.

        Returns:
            A Translator instance ready for use.
        """

    @abstractmethod
    def list_supported_locales(self) -> list[str]:
        """
        Enumerates all available language codes supported by the registry.

        Returns:
            A list of locale strings (e.g., ['de-DE', 'en-US']).
        """

    @abstractmethod
    def list_supported_themes(self, locale: str) -> list[str]:
        """
        Lists all themes available for a specific locale.

        Args:
            locale: The locale for which to check theme availability.

        Returns:
            A list of theme names (e.g., ['standard', 'fantasy']).
        """

    @property
    @abstractmethod
    def default_locale(self) -> str:
        """
        The system-wide fallback locale code.

        Returns:
            The default locale string.
        """
