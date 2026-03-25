"""Helpers for duplicate detection against local history."""

from __future__ import annotations

from dataclasses import dataclass
from difflib import SequenceMatcher

from src.schemas import JobRecord


@dataclass
class DuplicateCheckResult:
    is_duplicate: bool
    reason: str = ""
    matched_id: int | None = None
    matched_company: str = ""
    matched_job_title: str = ""
    similarity: float = 0.0


def normalize_text(value: str) -> str:
    return " ".join(value.strip().lower().split())


def similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, normalize_text(a), normalize_text(b)).ratio()


def looks_like_duplicate(record: JobRecord, history_rows: list[dict]) -> DuplicateCheckResult:
    source_url = normalize_text(record.source_url)
    company = normalize_text(record.company)
    job_title = normalize_text(record.job_title)

    for row in history_rows:
        history_url = normalize_text(str(row.get("source_url", "")))
        if source_url and history_url and source_url == history_url:
            return DuplicateCheckResult(
                is_duplicate=True,
                reason="来源链接重复",
                matched_id=row.get("id"),
                matched_company=str(row.get("company", "")),
                matched_job_title=str(row.get("job_title", "")),
                similarity=1.0,
            )

    for row in history_rows:
        history_company = normalize_text(str(row.get("company", "")))
        history_title = normalize_text(str(row.get("job_title", "")))
        if company and job_title and company == history_company and job_title == history_title:
            return DuplicateCheckResult(
                is_duplicate=True,
                reason="公司和岗位名称重复",
                matched_id=row.get("id"),
                matched_company=str(row.get("company", "")),
                matched_job_title=str(row.get("job_title", "")),
                similarity=1.0,
            )

    best_match: DuplicateCheckResult | None = None
    for row in history_rows:
        history_company_raw = str(row.get("company", ""))
        history_title_raw = str(row.get("job_title", ""))
        title_score = similarity(record.job_title, history_title_raw)
        company_score = similarity(record.company, history_company_raw)
        if title_score >= 0.9 and company_score >= 0.85:
            candidate = DuplicateCheckResult(
                is_duplicate=True,
                reason="公司和岗位名称高度相似",
                matched_id=row.get("id"),
                matched_company=history_company_raw,
                matched_job_title=history_title_raw,
                similarity=(title_score + company_score) / 2,
            )
            if best_match is None or candidate.similarity > best_match.similarity:
                best_match = candidate

    return best_match or DuplicateCheckResult(is_duplicate=False)
