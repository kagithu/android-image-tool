from __future__ import annotations

import json
from pathlib import Path

LOCALES = Path(__file__).resolve().parent.parent / "locales"


def load_language(language: str) -> dict[str, str]:
    path = LOCALES / f"{language}.json"
    if not path.is_file():
        raise FileNotFoundError(f"Locale file not found: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Invalid locale file: {path}")
    return data


LANG = {language: load_language(language) for language in ("en", "ja")}
