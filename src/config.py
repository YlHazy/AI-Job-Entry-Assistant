"""Project configuration constants."""

from __future__ import annotations

import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_EXCEL_PATH = PROJECT_ROOT / "data" / "job_board.xlsx"
DEFAULT_SHEET_NAME = "JobBoard"
PROMPTS_DIR = PROJECT_ROOT / "prompts"
DATA_DIR = PROJECT_ROOT / "data"
TEMPLATE_CACHE_PATH = DATA_DIR / "template_mappings.json"
HISTORY_DB_PATH = DATA_DIR / "job_history.db"
AUTH_DB_PATH = DATA_DIR / "auth.db"

Bailian_API_KEY_ENV = "OPENAI_API_KEY"
BAILIAN_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
BAILIAN_MODEL = os.getenv("JOB_AGENT_MODEL", "qwen-plus")
OCR_BACKEND = os.getenv("JOB_AGENT_OCR_BACKEND", "pytesseract")
AUTH_SESSION_DAYS = int(os.getenv("JOB_AGENT_AUTH_SESSION_DAYS", "14"))


def get_bailian_api_key() -> str:
    return os.getenv(Bailian_API_KEY_ENV, "").strip()
