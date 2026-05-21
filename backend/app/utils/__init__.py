"""app/utils/__init__.py"""
from __future__ import annotations

import unicodedata


def normalize_vi(text: str | None) -> str | None:
    """Strip Vietnamese (and other) diacritics and lowercase.

    'Lập Trình' -> 'lap trinh'
    Returns None when input is None (safe to use as a SQLite custom function).
    """
    if text is None:
        return None
    return (
        unicodedata.normalize("NFD", text)
        .encode("ascii", "ignore")
        .decode("ascii")
        .lower()
    )
