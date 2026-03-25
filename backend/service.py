"""Service layer for API endpoints."""

from __future__ import annotations

from src.agent import JobIntakeAgent
from src.auth_store import AuthenticationError, AuthStore, ConflictError
from src.deduper import DuplicateCheckResult, looks_like_duplicate
from src.excel_writer import ExcelWriteError, append_job_record
from src.history_store import HistoryStore
from src.ocr_reader import OCRUnavailableError, extract_text_from_image_bytes
from src.path_utils import normalize_sheet_name, normalize_user_text
from src.schemas import AgentRunResult, JobRecord
from src.web_fetcher import WebFetchError


class JobIntakeService:
    """Facade that coordinates agent runs, dedupe checks, history, and writing."""

    def __init__(self, history: HistoryStore | None = None, auth: AuthStore | None = None) -> None:
        self.agent = JobIntakeAgent()
        self.history = history or HistoryStore()
        self.auth = auth or AuthStore()

    def register(self, username: str, password: str) -> tuple[dict, str]:
        user = self.auth.register(username=username, password=password)
        token = self.auth.create_session(user["id"])
        return user, token

    def login(self, username: str, password: str) -> tuple[dict, str]:
        user = self.auth.authenticate(username=username, password=password)
        token = self.auth.create_session(user["id"])
        return user, token

    def current_user(self, token: str) -> dict:
        return self.auth.get_user_by_token(token)

    def logout(self, token: str) -> None:
        self.auth.revoke_session(token)

    def analyze(
        self,
        user_id: int,
        mode: str,
        source_platform: str,
        source_url: str,
        raw_text: str,
        image_bytes: bytes | None = None,
    ) -> tuple[AgentRunResult, DuplicateCheckResult]:
        normalized_url = normalize_user_text(source_url)

        if mode == "text":
            if not raw_text.strip():
                raise ValueError("文本模式下请提供 JD 文本。")
            run = self.agent.run(
                raw_text=raw_text,
                source_platform=source_platform,
                source_url=normalized_url,
                prefer_llm=True,
            )
        elif mode == "url":
            if not normalized_url:
                raise ValueError("链接模式下请提供岗位链接。")
            run = self.agent.run_from_url(
                url=normalized_url,
                source_platform=source_platform,
                prefer_llm=True,
            )
        elif mode == "image":
            if not image_bytes:
                raise ValueError("截图模式下请上传图片。")
            ocr = extract_text_from_image_bytes(image_bytes)
            run = self.agent.run(
                raw_text=ocr.text,
                source_platform=source_platform,
                source_url=normalized_url,
                prefer_llm=True,
            )
        else:
            raise ValueError(f"Unsupported mode: {mode}")

        candidates = self.history.search_candidates(run.record, user_id=user_id)
        duplicate = looks_like_duplicate(run.record, candidates)
        return run, duplicate

    def write(self, user_id: int, record: JobRecord, excel_path: str, sheet_name: str) -> str:
        normalized_path = normalize_user_text(excel_path)
        normalized_sheet = normalize_sheet_name(sheet_name)
        if not normalized_path:
            raise ValueError("请提供 Excel 路径。")

        saved_path = append_job_record(
            excel_path=normalized_path,
            record=record,
            sheet_name=normalized_sheet,
        )
        self.history.insert(record, user_id=user_id)
        return str(saved_path)

    def recent_history(self, user_id: int, limit: int = 20) -> list[dict]:
        return self.history.recent(limit=limit, user_id=user_id)

    def search_history(self, user_id: int, query: str, priority: str, match_direction: str, limit: int) -> list[dict]:
        return self.history.search(
            query=query,
            priority=priority,
            match_direction=match_direction,
            limit=limit,
            user_id=user_id,
        )

    def history_by_id(self, user_id: int, record_id: int) -> dict | None:
        return self.history.get_by_id(record_id, user_id=user_id)

    def bootstrap(self, user_id: int) -> dict:
        return {
            "llm_configured": bool(self.agent.analyzer.is_configured),
            "history_count": self.history.count(user_id=user_id),
            "user_count": self.auth.count_users(),
        }


def map_known_error(exc: Exception) -> tuple[str, str, list[str]]:
    if isinstance(exc, AuthenticationError):
        return (
            "UNAUTHORIZED",
            str(exc),
            ["请重新登录，或确认账号密码是否正确。"],
        )
    if isinstance(exc, ConflictError):
        return (
            "CONFLICT",
            str(exc),
            ["请更换用户名，或直接使用已有账号登录。"],
        )
    if isinstance(exc, ValueError):
        return (
            "INVALID_INPUT",
            str(exc),
            ["检查输入模式和必填字段。"],
        )
    if isinstance(exc, WebFetchError):
        return (
            "FETCH_ERROR",
            str(exc),
            ["确认链接可访问。", "确认网络未拦截目标站点。"],
        )
    if isinstance(exc, OCRUnavailableError):
        return (
            "OCR_UNAVAILABLE",
            str(exc),
            ["安装 pytesseract。", "安装本地 Tesseract OCR 引擎。"],
        )
    if isinstance(exc, ExcelWriteError):
        return (
            "EXCEL_WRITE_ERROR",
            str(exc),
            exc.reasons,
        )
    return (
        "INTERNAL_ERROR",
        str(exc),
        ["请查看后端日志定位详细原因。"],
    )
