"""FastAPI backend for the Job Intake Assistant."""

from __future__ import annotations

from contextvars import ContextVar
from uuid import uuid4

from fastapi import FastAPI, File, Form, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.api_models import HistoryQuery, WriteRequest
from backend.errors import ApiResponse, error_response, success_response
from backend.service import JobIntakeService, map_known_error

app = FastAPI(title="Job Intake Assistant API", version="1.0.0")
service = JobIntakeService()
request_id_ctx: ContextVar[str] = ContextVar("request_id", default="unknown")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = request.headers.get("x-request-id") or uuid4().hex[:12]
    request_id_ctx.set(request_id)
    response = await call_next(request)
    response.headers["x-request-id"] = request_id
    return response


def current_request_id() -> str:
    return request_id_ctx.get()


@app.exception_handler(Exception)
async def unhandled_exception_handler(_: Request, exc: Exception):
    code, message, suggestions = map_known_error(exc)
    payload = error_response(
        request_id=current_request_id(),
        code=code if code != "INVALID_INPUT" else "INTERNAL_ERROR",
        message=message,
        suggestions=suggestions,
    )
    return JSONResponse(status_code=500, content=payload.model_dump())


@app.get("/api/health", response_model=ApiResponse)
def health() -> ApiResponse:
    return success_response(request_id=current_request_id(), data={"status": "ok"})


@app.get("/api/bootstrap", response_model=ApiResponse)
def bootstrap() -> ApiResponse:
    return success_response(request_id=current_request_id(), data=service.bootstrap())


@app.post("/api/analyze", response_model=ApiResponse)
async def analyze(
    mode: str = Form("text"),
    source_platform: str = Form(""),
    source_url: str = Form(""),
    raw_text: str = Form(""),
    image_file: UploadFile | None = File(None),
) -> ApiResponse:
    try:
        image_bytes = await image_file.read() if image_file else None
        run, duplicate = service.analyze(
            mode=mode,
            source_platform=source_platform,
            source_url=source_url,
            raw_text=raw_text,
            image_bytes=image_bytes,
        )
        return success_response(
            request_id=current_request_id(),
            data={
                "record": run.record.model_dump(),
                "steps": [step.model_dump() for step in run.steps],
                "duplicate": duplicate.__dict__,
            },
        )
    except Exception as exc:  # pragma: no cover
        code, message, suggestions = map_known_error(exc)
        payload = error_response(
            request_id=current_request_id(),
            code=code,
            message=message,
            suggestions=suggestions,
        )
        return JSONResponse(status_code=400, content=payload.model_dump())


@app.post("/api/write", response_model=ApiResponse)
def write(payload: WriteRequest) -> ApiResponse:
    try:
        saved_path = service.write(
            record=payload.record,
            excel_path=payload.excel_path,
            sheet_name=payload.sheet_name,
        )
        return success_response(request_id=current_request_id(), data={"saved_path": saved_path})
    except Exception as exc:  # pragma: no cover
        code, message, suggestions = map_known_error(exc)
        payload = error_response(
            request_id=current_request_id(),
            code=code,
            message=message,
            suggestions=suggestions,
        )
        return JSONResponse(status_code=400, content=payload.model_dump())


@app.get("/api/history", response_model=ApiResponse)
def history(query: str = "", priority: str = "", match_direction: str = "", limit: int = 50) -> ApiResponse:
    try:
        payload = HistoryQuery(query=query, priority=priority, match_direction=match_direction, limit=limit)
        rows = service.search_history(
            query=payload.query,
            priority=payload.priority,
            match_direction=payload.match_direction,
            limit=payload.limit,
        )
        return success_response(request_id=current_request_id(), data={"rows": rows})
    except Exception as exc:  # pragma: no cover
        code, message, suggestions = map_known_error(exc)
        payload = error_response(
            request_id=current_request_id(),
            code=code,
            message=message,
            suggestions=suggestions,
        )
        return JSONResponse(status_code=400, content=payload.model_dump())


@app.get("/api/history/{record_id}", response_model=ApiResponse)
def history_detail(record_id: int) -> ApiResponse:
    try:
        row = service.history_by_id(record_id)
        if not row:
            payload = error_response(
                request_id=current_request_id(),
                code="NOT_FOUND",
                message=f"历史记录不存在：{record_id}",
                suggestions=["确认记录 ID 是否正确。"],
            )
            return JSONResponse(status_code=404, content=payload.model_dump())
        return success_response(request_id=current_request_id(), data={"row": row})
    except Exception as exc:  # pragma: no cover
        code, message, suggestions = map_known_error(exc)
        payload = error_response(
            request_id=current_request_id(),
            code=code,
            message=message,
            suggestions=suggestions,
        )
        return JSONResponse(status_code=400, content=payload.model_dump())
