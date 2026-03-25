"""Pydantic schemas for the job intake assistant."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class AgentStep(BaseModel):
    """A single agent step with inputs, outputs, and supporting context."""

    name: str
    skill: str = ""
    status: str = "completed"
    summary: str = ""
    evidence: list[str] = Field(default_factory=list)
    output: dict[str, Any] = Field(default_factory=dict)


class AgentRunResult(BaseModel):
    """Container for the final record and the execution trace."""

    record: "JobRecord"
    steps: list[AgentStep] = Field(default_factory=list)


class ExcelTemplateMapping(BaseModel):
    """Resolved mapping from canonical fields to a specific Excel template."""

    workbook_key: str
    target_sheet: str
    header_row: int
    data_start_row: int
    key_columns: dict[str, int] = Field(default_factory=dict)
    confidence: float = 0.0
    warnings: list[str] = Field(default_factory=list)
    detection_mode: str = "rules"


class JobRecord(BaseModel):
    """Structured job information ready for review and Excel export."""

    input_type: str = "text"
    source_platform: str = ""
    source_url: str = ""
    company: str = ""
    job_title: str = ""
    location: str = ""
    is_internship: bool | None = None
    role_category: str = ""
    match_direction: str = ""
    priority: str = ""
    recommend_resume_customization: str = ""
    jd_summary: str = ""
    keywords: list[str] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)
    education_requirement: str = ""
    notes: str = ""
    raw_text: str = ""
    category_reason: str = ""
    evidence_keywords: list[str] = Field(default_factory=list)
    match_score: int = 0
    match_reason: str = ""
    main_gap: str = ""
    resume_focus: list[str] = Field(default_factory=list)
    short_note: str = ""

    def to_excel_row(self) -> dict[str, Any]:
        """Return a normalized mapping used by generic writers."""

        return {
            "录入时间": "",
            "公司": self.company,
            "岗位名称": self.job_title,
            "岗位类别": self.role_category,
            "匹配方向": self.match_direction,
            "工作地点": self.location,
            "是否实习": _format_bool(self.is_internship),
            "来源平台": self.source_platform,
            "来源链接": self.source_url,
            "优先级": self.priority,
            "是否建议单独改简历": self.recommend_resume_customization,
            "关键词命中": "、".join(self.keywords),
            "JD 摘要": self.jd_summary,
            "主要技能要求": "、".join(self.skills),
            "学历要求": self.education_requirement,
            "是否决定投递": "",
            "投递日期": "",
            "当前状态": "",
            "跟进记录": "",
            "面试问题记录": "",
            "挂点分析": self.main_gap,
            "备注": self.short_note or self.notes,
        }


def _format_bool(value: bool | None) -> str:
    if value is True:
        return "是"
    if value is False:
        return "否"
    return ""
