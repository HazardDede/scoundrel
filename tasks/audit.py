import os
import sys
from pathlib import Path

from invoke import task

from scoundrel.localization.json import JsonRegistry
from scoundrel.localization.manifest import TranslationManifest
from tasks.config import (
    PROJECT_ROOT_PATH
)

# Colors and icons for a pretty console output
CHECK = "\033[92m✔\033[0m"  # Green check
CROSS = "\033[91m✘\033[0m"  # Red cross
BOLD = "\033[1m"
RESET = "\033[0m"


TRANSLATIONS_PATH = os.path.join(PROJECT_ROOT_PATH, 'assets/translations')


@task(default=True)
def run(ctx):
    base_path = Path(TRANSLATIONS_PATH)
    manifest_path = base_path / "manifest.txt"

    if not manifest_path.exists():
        print(f"{CROSS} {BOLD}Error:{RESET} Manifest file not found at {manifest_path}")
        sys.exit(1)

    registry = JsonRegistry(base_path)
    manifest = TranslationManifest.from_file(manifest_path)

    print(f"{BOLD}Starting Translation Audit...{RESET}")
    print(f"Loaded {len(manifest.required_keys)} keys from manifest.\n")

    results = manifest.audit_registry(registry)

    total_errors = 0

    # English comment: Iterate through all locale/theme combinations
    for (locale, theme), missing in results.items():
        theme_name = theme if theme else "Core"
        context = f"{locale} [{theme_name}]"

        if not missing:
            print(f"{CHECK} {context.ljust(20)} | All keys present.")
        else:
            total_errors += len(missing)
            print(f"{CROSS} {context.ljust(20)} | {BOLD}{len(missing)} missing keys:{RESET}")
            for key in missing:
                print(f"    - {key}")

    print("-" * 40)
    if total_errors == 0:
        print(f"{BOLD}Audit passed!{RESET} All translations are complete.")
        sys.exit(0)
    else:
        print(f"{BOLD}Audit failed!{RESET} Total missing keys: {total_errors}")
        sys.exit(1)
