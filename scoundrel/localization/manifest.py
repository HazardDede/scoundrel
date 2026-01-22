"""
Translation auditing and manifest management.

This module provides the tools to ensure that all required translation keys
are present across all supported locales and themes. It acts as a validation
layer between the application requirements and the actual translation assets.

The 'TranslationManifest' serves as a source of truth, typically loaded from
a plain text file containing one key per line, allowing for automated
consistency checks (audits) in CI/CD pipelines or development tools.
"""
from pathlib import Path
from typing import Tuple

from .base import Translator, TranslationRegistry


TLocale = str
TTheme = str
TTranslationKey = str

AuditResult = dict[Tuple[TLocale, TTheme | None], list[TTranslationKey]]


class TranslationManifest:
    """Central authority for all translation keys used in the app."""

    def __init__(self, keys: set[str]):
        self.required_keys = keys

    @classmethod
    def from_file(cls, file_path: Path) -> "TranslationManifest":
        """Loads required keys from a simple text file (one key per line)."""
        if not file_path.exists():
            return cls(set())

        with open(file_path, "r", encoding="utf-8") as f:
            # Removes comment (lines starting with '#') and empty lines
            keys = {line.strip() for line in f if line.strip() and not line.startswith("#")}
        return cls(keys)

    def audit_translator(self, translator: Translator) -> list[str]:
        """Returns a list of missing keys for a given translator."""
        return [key for key in self.required_keys if not translator.supports(key)]

    def audit_registry(self, registry: TranslationRegistry) -> AuditResult:
        """Runs a full audit on every translator provided by the registry."""
        locales = registry.list_supported_locales()
        results = {}

        for locale in locales:
            themes: list[str | None] = [None] + registry.list_supported_themes(locale)
            for theme in themes:
                translator = registry.get_translator(locale, theme)
                missing = self.audit_translator(translator)
                results[(locale, theme)] = missing

        return results
