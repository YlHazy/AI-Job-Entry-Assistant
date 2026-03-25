"""FastAPI backend for the Job Intake Assistant."""

from __future__ import annotations

from contextvars import ContextVar
from uuid import uuid4

from fastapi import Depends, FastAPI, File, Form, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.api_models import AuthRequest, HistoryQuery, WriteRequest
from backend.errors import ApiResponse, error_response, success_response
from backend.service import JobIntakeService, map_known_error
from src.auth_store import AuthenticationError, ConflictError

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


def _json_error(status_code: int, code: str, message: str, suggestions: list[str]) -> JSONResponse:
    payload = error_response(
        request_id=current_request_id(),
        code=code,
        message=message,
        suggestions=suggestions,
    )
    return JSONResponse(status_code=status_code, content=payload.model_dump())


def _extract_bearer_token(request: Request) -> str:
    auth_header = request.headers.get("authorization", "")
    if not auth_header.startswith("Bearer "):
        raise AuthenticationError("缺少 Bearer 登录凭证。")
    return auth_header.split(" ", 1)[1].strip()


def require_user(request: Request) -> dict:
    token = _extract_bearer_token(request)
    return service.current_user(token)


@app.exception_handler(Exception)
async def unhandled_exception_handler(_: Request, exc: Exception):
    code, message, suggestions = map_known_error(exc)
    return _json_error(
        500,
        code if code != "INVALID_INPUT" else "INTERNAL_ERROR",
        message,
        suggestions,
    )


@app.exception_handler(AuthenticationError)
async def authentication_exception_handler(_: Request, exc: AuthenticationError):
    code, message, suggestions = map_known_error(exc)
    return _json_error(401, code, message, suggestions)


@app.exception_handler(ConflictError)
async def conflict_exception_handler(_: Request, exc: ConflictError):
    code, message, suggestions = map_known_error(exc)
    return _json_error(409, code, message, suggestions)


@app.get("/api/health", response_model=ApiResponse)
def health() -> ApiResponse:
    return success_response(request_id=current_request_id(), data={"status": "ok"})


@app.post("/api/auth/register", response_model=ApiResponse)
def register(payload: AuthRequest) -> ApiResponse | JSONResponse:
    try:
        user, token = service.register(payload.username, payload.password)
        return success_response(request_id=current_request_id(), data={"user": user, "token": token})
    except Exception as exc:  # pragma: no cover
        code, message, suggestions = map_known_error(exc)
        status_code = 409 if code == "CONFLICT" else 400
        return _json_error(status_code, code, message, suggestions)


@app.post("/api/auth/login", response_model=ApiResponse)
def login(payload: AuthRequest) -> ApiResponse | JSONResponse:
    try:
        user, token = service.login(payload.username, payload.password)
        return success_response(request_id=current_request_id(), data={"user": user, "token": token})
    except Exception as exc:  # pragma: no cover
        code, message, suggestions = map_known_error(exc)
        status_code = 401 if code == "UNAUTHORIZED" else 400
        return _json_error(status_code, code, message, suggestions)


@app.get("/api/auth/me", response_model=ApiResponse)
def me(user: dict = Depends(require_user)) -> ApiResponse:
    return success_response(request_id=current_request_id(), data={"user": user})


@app.post("/api/auth/logout", response_model=ApiResponse)
def logout(request: Request, _: dict = Depends(require_user)) -> ApiResponse:
    token = _extract_bearer_token(request)
    service.logout(token)
    return success_response(request_id=current_request_id(), data={"logged_out": True})


@app.get("/api/bootstrap", response_model=ApiResponse)
def bootstrap(user: dict = Depends(require_user)) -> ApiResponse:
    return success_response(request_id=current_request_id(), data=service.bootstrap(user_id=user["id"]))


@app.post("/api/analyze", response_model=ApiResponse)
async def analyze(
    user: dict = Depends(require_user),
    mode: str = Form("text"),
    source_platform: str = Form(""),
    source_url: str = Form(""),
    raw_text: str = Form(""),
    image_file: UploadFile | None = File(None),
) -> ApiResponse:
    try:
        image_bytes = await image_file.read() if image_file else None
        run, duplicate = service.analyze(
            user_id=user["id"],
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
        status_code = 401 if code == "UNAUTHORIZED" else 400
        return _json_error(status_code, code, message, suggestions)


@app.post("/api/write", response_model=ApiResponse)
def write(payload: WriteRequest, user: dict = Depends(require_user)) -> ApiResponse | JSONResponse:
    try:
        saved_path = service.write(
            user_id=user["id"],
            record=payload.record,
            excel_path=payload.excel_path,
            sheet_name=payload.sheet_name,
        )
        return success_response(request_id=current_request_id(), data={"saved_path": saved_path})
    except Exception as exc:  # pragma: no cover
        code, message, suggestions = map_known_error(exc)
        status_code = 401 if code == "UNAUTHORIZED" else 400
        return _json_error(status_code, code, message, suggestions)


@app.get("/api/history", response_model=ApiResponse)
def history(
    query: str = "",
    priority: str = "",
    match_direction: str = "",
    limit: int = 50,
    user: dict = Depends(require_user),
) -> ApiResponse | JSONResponse:
    try:
        payload = HistoryQuery(query=query, priority=priority, match_direction=match_direction, limit=limit)
        rows = service.search_history(
            user_id=user["id"],
            query=payload.query,
            priority=payload.priority,
            match_direction=payload.match_direction,
            limit=payload.limit,
        )
        return success_response(request_id=current_request_id(), data={"rows": rows})
    except Exception as exc:  # pragma: no cover
        code, message, suggestions = map_known_error(exc)
        status_code = 401 if code == "UNAUTHORIZED" else 400
        return _json_error(status_code, code, message, suggestions)


@app.get("/api/history/{record_id}", response_model=ApiResponse)
def history_detail(record_id: int, user: dict = Depends(require_user)) -> ApiResponse | JSONResponse:
    try:
        row = service.history_by_id(user_id=user["id"], record_id=record_id)
        if not row:
            return _json_error(404, "NOT_FOUND", f"历史记录不存在：{record_id}", ["确认记录 ID 是否正确。"])
        return success_response(request_id=current_request_id(), data={"row": row})
    except Exception as exc:  # pragma: no cover
        code, message, suggestions = map_known_error(exc)
        status_code = 401 if code == "UNAUTHORIZED" else 400
        return _json_error(status_code, code, message, suggestions)
