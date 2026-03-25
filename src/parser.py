"""Rule-based JD parser for V1."""

from __future__ import annotations

import re
from collections import Counter

from src.schemas import JobRecord

SKILL_TERMS = [
    "Python",
    "SQL",
    "RAG",
    "Agent",
    "LLM",
    "Prompt Engineering",
    "OpenAI",
    "LangChain",
    "FastAPI",
    "Flask",
    "Pandas",
    "Streamlit",
    "Excel",
    "AIGC",
    "PRD",
    "Figma",
    "Axure",
    "埋点",
    "数据分析",
    "工作流",
    "向量数据库",
    "提示词",
    "产品设计",
]

KEYWORD_TERMS = [
    "AI Agent",
    "LLM",
    "RAG",
    "AIGC",
    "Prompt",
    "工作流",
    "Python",
    "后端",
    "数据分析",
    "产品设计",
    "用户研究",
    "PRD",
    "平台产品",
    "技术方案",
    "自动化",
]

LOCATION_HINTS = [
    "北京",
    "上海",
    "深圳",
    "广州",
    "杭州",
    "成都",
    "南京",
    "苏州",
    "武汉",
    "西安",
    "远程",
]

EDUCATION_PATTERNS = [
    r"(本科及以上)",
    r"(硕士及以上)",
    r"(本科以上)",
    r"(硕士以上)",
    r"(大专及以上)",
    r"(学历不限)",
]

JOB_TITLE_PATTERNS = [
    re.compile(r"(AI\s*Agent[\u4e00-\u9fffA-Za-z0-9/（）()·\- ]{0,20})"),
    re.compile(r"(AI[\u4e00-\u9fffA-Za-z0-9/（）()·\- ]{0,20}(工程师|开发|产品经理|实习生))"),
    re.compile(r"((算法|后端|产品|技术产品|平台产品)[\u4e00-\u9fffA-Za-z0-9/（）()·\- ]{0,20}(实习生|工程师|开发|产品经理))"),
    re.compile(r"(职位名称[:：]\s*[^\n]{2,40})"),
]

COMPANY_PATTERNS = [
    re.compile(r"(公司[:：]\s*[^\n]{2,40})"),
    re.compile(r"(企业[:：]\s*[^\n]{2,40})"),
    re.compile(r"([A-Za-z0-9\u4e00-\u9fff]{2,20}(科技|网络|信息|智能|软件|集团|公司))"),
]


def parse_job_text(raw_text: str, source_platform: str = "", source_url: str = "") -> JobRecord:
    """Parse a JD text into a partially filled job record."""

    normalized = normalize_text(raw_text)
    company = extract_company(normalized)
    job_title = extract_job_title(normalized)
    location = extract_location(normalized)
    is_internship = infer_is_internship(normalized, job_title)
    education_requirement = extract_education_requirement(normalized)
    keywords = extract_terms(normalized, KEYWORD_TERMS, limit=8)
    skills = extract_terms(normalized, SKILL_TERMS, limit=10)
    jd_summary = build_summary(normalized)

    return JobRecord(
        source_platform=source_platform.strip(),
        source_url=source_url.strip(),
        company=company,
        job_title=job_title,
        location=location,
        is_internship=is_internship,
        jd_summary=jd_summary,
        keywords=keywords,
        skills=skills,
        education_requirement=education_requirement,
        raw_text=raw_text.strip(),
    )


def normalize_text(text: str) -> str:
    compact = text.replace("\r\n", "\n").replace("\r", "\n")
    compact = re.sub(r"[ \t]+", " ", compact)
    compact = re.sub(r"\n{2,}", "\n", compact)
    return compact.strip()


def extract_company(text: str) -> str:
    for pattern in COMPANY_PATTERNS:
        match = pattern.search(text)
        if not match:
            continue
        value = match.group(1)
        return clean_labeled_value(value)
    return ""


def extract_job_title(text: str) -> str:
    for pattern in JOB_TITLE_PATTERNS:
        match = pattern.search(text)
        if not match:
            continue
        return clean_labeled_value(match.group(1))
    return ""


def extract_location(text: str) -> str:
    for city in LOCATION_HINTS:
        if city in text:
            return city
    match = re.search(r"(工作地点|地点|Base)[:：]?\s*([^\n，,]{2,20})", text, flags=re.IGNORECASE)
    if match:
        return match.group(2).strip()
    return ""


def infer_is_internship(text: str, job_title: str = "") -> bool | None:
    combined = f"{job_title}\n{text}"
    if "实习" in combined or "intern" in combined.lower():
        return True
    if any(token in combined for token in ["校招", "正式", "社招", "全职"]):
        return False
    return None


def extract_education_requirement(text: str) -> str:
    for pattern in EDUCATION_PATTERNS:
        match = re.search(pattern, text)
        if match:
            return match.group(1)
    match = re.search(r"(本科|硕士|博士|大专)[^\n，。,；;]{0,8}(优先|以上|及以上)?", text)
    if match:
        return match.group(0)
    return ""


def extract_terms(text: str, terms: list[str], limit: int) -> list[str]:
    lowered = text.lower()
    counter: Counter[str] = Counter()
    for term in terms:
        hits = lowered.count(term.lower())
        if hits:
            counter[term] = hits
    return [term for term, _ in counter.most_common(limit)]


def build_summary(text: str, max_length: int = 120) -> str:
    lines = [line.strip(" -•\t") for line in text.splitlines() if line.strip()]
    if not lines:
        return ""
    summary = "；".join(lines[:3])
    if len(summary) > max_length:
        return summary[: max_length - 1].rstrip("；，, ") + "…"
    return summary


def clean_labeled_value(value: str) -> str:
    return re.sub(r"^(公司|企业|职位名称|岗位名称|岗位|职位)[:：]\s*", "", value).strip("：: ")
