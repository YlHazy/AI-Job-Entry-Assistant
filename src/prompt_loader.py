"""Helpers for loading local prompt templates."""

from __future__ import annotations

from pathlib import Path

from src.config import PROMPTS_DIR


def load_prompt(name: str) -> str:
    path = PROMPTS_DIR / name
    return Path(path).read_text(encoding="utf-8")
