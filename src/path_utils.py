"""Utilities for normalizing user-provided file paths and sheet names."""

from __future__ import annotations


def normalize_user_text(value: str) -> str:
    text = (value or "").strip()
    if len(text) >= 2 and text[0] == text[-1] and text[0] in {'"', "'"}:
        text = text[1:-1].strip()
    return text


def normalize_sheet_name(value: str) -> str:
    return normalize_user_text(value)
