"""Pydantic request/response models for backend APIs."""

from __future__ import annotations

from pydantic import BaseModel, Field

from src.schemas import JobRecord


class AnalyzeRequest(BaseModel):
    mode: str = "text"
    source_platform: str = ""
    source_url: str = ""
    raw_text: str = ""


class WriteRequest(BaseModel):
    record: JobRecord
    excel_path: str
    sheet_name: str = ""


class HistoryQuery(BaseModel):
    query: str = ""
    priority: str = ""
    match_direction: str = ""
    limit: int = Field(default=50, ge=1, le=200)
