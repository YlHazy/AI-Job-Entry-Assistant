"""LLM analyzer backed by Alibaba Cloud Bailian OpenAI-compatible API."""

from __future__ import annotations

import json
from typing import Any

from openai import OpenAI

from src.config import BAILIAN_BASE_URL, BAILIAN_MODEL, get_bailian_api_key
from src.parser import parse_job_text
from src.prompt_loader import load_prompt
from src.schemas import AgentStep, JobRecord


SYSTEM_PROMPT = (
    "You are a job intake assistant. "
    "Return exactly one JSON object and nothing else. "
    "Do not wrap the JSON in Markdown."
)


class BailianAnalyzer:
    """Use a Qwen model to produce a structured JD analysis."""

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str = BAILIAN_BASE_URL,
        model: str = BAILIAN_MODEL,
        client: OpenAI | None = None,
    ) -> None:
        self.api_key = (api_key or get_bailian_api_key()).strip()
        self.base_url = base_url
        self.model = model
        self.client = client or (OpenAI(api_key=self.api_key, base_url=self.base_url) if self.api_key else None)

    @property
    def is_configured(self) -> bool:
        return bool(self.client)

    def analyze(self, raw_text: str, source_platform: str = "", source_url: str = "") -> tuple[JobRecord, AgentStep]:
        if not self.client:
            raise RuntimeError("Bailian analyzer is not configured. Missing OPENAI_API_KEY.")

        baseline = parse_job_text(raw_text, source_platform=source_platform, source_url=source_url)
        prompt_template = load_prompt("full_job_analysis.md")
        user_prompt = prompt_template.replace("{{raw_text}}", raw_text.strip())

        response = self.client.chat.completions.create(
            model=self.model,
            temperature=0.2,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
        )

        content = response.choices[0].message.content or ""
        payload = parse_json_content(content)
        record = merge_payload_into_record(
            baseline=baseline,
            payload=payload,
            source_platform=source_platform,
            source_url=source_url,
            raw_text=raw_text,
        )

        step = AgentStep(
            name="LLM 综合分析",
            skill="prompts/full_job_analysis.md + qwen",
            summary="Used Bailian Qwen to produce a structured analysis with rule-based field repair.",
            evidence=[
                f"model={self.model}",
                f"match_score={record.match_score}",
                f"role_category={record.role_category}",
            ],
            output=payload,
        )
        return record, step


def merge_payload_into_record(
    baseline: JobRecord,
    payload: dict[str, Any],
    source_platform: str,
    source_url: str,
    raw_text: str,
) -> JobRecord:
    return baseline.model_copy(
        update={
            "source_platform": source_platform.strip(),
            "source_url": source_url.strip(),
            "company": _pick_string(payload.get("company"), baseline.company),
            "job_title": _pick_string(payload.get("job_title"), baseline.job_title),
            "location": _pick_string(payload.get("location"), baseline.location),
            "is_internship": _pick_optional_bool(payload.get("is_internship"), baseline.is_internship),
            "jd_summary": _pick_string(payload.get("jd_summary"), baseline.jd_summary),
            "keywords": _pick_list(payload.get("keywords"), baseline.keywords),
            "skills": _pick_list(payload.get("skills"), baseline.skills),
            "education_requirement": _pick_string(payload.get("education_requirement"), baseline.education_requirement),
            "role_category": _pick_string(payload.get("role_category"), baseline.role_category),
            "category_reason": _pick_string(payload.get("category_reason"), baseline.category_reason),
            "evidence_keywords": _pick_list(payload.get("evidence_keywords"), baseline.evidence_keywords),
            "match_direction": _pick_string(payload.get("match_direction"), baseline.match_direction),
            "match_score": _pick_int(payload.get("match_score"), baseline.match_score),
            "match_reason": _pick_string(payload.get("match_reason"), baseline.match_reason),
            "main_gap": _pick_string(payload.get("main_gap"), baseline.main_gap),
            "priority": normalize_priority(_pick_string(payload.get("priority"), baseline.priority)),
            "recommend_resume_customization": normalize_yes_no(
                _pick_string(payload.get("custom_resume_needed"), baseline.recommend_resume_customization)
            ),
            "resume_focus": _pick_list(payload.get("resume_focus"), baseline.resume_focus),
            "short_note": _pick_string(payload.get("short_note"), baseline.short_note),
            "raw_text": raw_text.strip(),
        }
    )


def parse_json_content(content: str) -> dict[str, Any]:
    cleaned = content.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.removeprefix("```json").removeprefix("```JSON").removeprefix("```").strip()
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3].strip()
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("Model response does not contain a valid JSON object.")
    return json.loads(cleaned[start : end + 1])


def normalize_yes_no(value: str) -> str:
    lowered = value.strip().lower()
    if lowered in {"yes", "true", "1", "是"}:
        return "是"
    if lowered in {"no", "false", "0", "否"}:
        return "否"
    return value.strip()


def normalize_priority(value: str) -> str:
    mapping = {
        "high": "高",
        "medium": "中",
        "mid": "中",
        "low": "低",
    }
    lowered = value.strip().lower()
    return mapping.get(lowered, value.strip())


def _to_string_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str) and value.strip():
        normalized = value.replace(",", "、").replace("，", "、").replace("\n", "、")
        return [item.strip() for item in normalized.split("、") if item.strip()]
    return []


def _to_optional_bool(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"true", "yes", "是"}:
            return True
        if lowered in {"false", "no", "否"}:
            return False
    return None


def _pick_string(value: Any, fallback: str) -> str:
    text = str(value).strip() if value is not None else ""
    return text or fallback


def _pick_list(value: Any, fallback: list[str]) -> list[str]:
    parsed = _to_string_list(value)
    return parsed or fallback


def _pick_optional_bool(value: Any, fallback: bool | None) -> bool | None:
    parsed = _to_optional_bool(value)
    return fallback if parsed is None else parsed


def _pick_int(value: Any, fallback: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return fallback
