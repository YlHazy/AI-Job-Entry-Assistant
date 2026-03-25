"""Shared API response models and helpers."""

from __future__ import annotations

from datetime import datetime, timezone

from pydantic import BaseModel, Field


class ApiError(BaseModel):
    """Serializable API error with suggestions."""

    code: str
    message: str
    suggestions: list[str] = Field(default_factory=list)


class ApiResponse(BaseModel):
    """Standard API response envelope."""

    ok: bool
    request_id: str
    timestamp: str
    data: dict | None = None
    error: ApiError | None = None


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def error_response(
    *,
    request_id: str,
    code: str,
    message: str,
    suggestions: list[str] | None = None,
) -> ApiResponse:
    return ApiResponse(
        ok=False,
        request_id=request_id,
        timestamp=utc_now_iso(),
        data=None,
        error=ApiError(code=code, message=message, suggestions=suggestions or []),
    )


def success_response(*, request_id: str, data: dict) -> ApiResponse:
    return ApiResponse(
        ok=True,
        request_id=request_id,
        timestamp=utc_now_iso(),
        data=data,
        error=None,
    )
