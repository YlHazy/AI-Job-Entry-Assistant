"""Agent-style orchestration for the job intake workflow."""

from __future__ import annotations

from pathlib import Path

from src.classifier import analyze_match_direction, analyze_priority, analyze_role_category
from src.config import PROJECT_ROOT
from src.llm_analyzer import BailianAnalyzer
from src.parser import parse_job_text
from src.schemas import AgentRunResult, AgentStep, JobRecord
from src.web_fetcher import fetch_job_page_text


class JobIntakeAgent:
    """Coordinate the JD intake workflow as a sequence of explicit skills."""

    def __init__(self, project_root: Path | None = None, analyzer: BailianAnalyzer | None = None) -> None:
        self.project_root = project_root or PROJECT_ROOT
        self.analyzer = analyzer or BailianAnalyzer()
        self.fetcher = fetch_job_page_text

    def run(
        self,
        raw_text: str,
        source_platform: str = "",
        source_url: str = "",
        prefer_llm: bool = True,
    ) -> AgentRunResult:
        if prefer_llm and self.analyzer.is_configured:
            try:
                llm_record, llm_step = self.analyzer.analyze(
                    raw_text,
                    source_platform=source_platform,
                    source_url=source_url,
                )
                return AgentRunResult(record=llm_record, steps=[llm_step, self._build_review_step(llm_record, "llm")])
            except Exception as exc:
                fallback = self._run_rule_pipeline(raw_text, source_platform=source_platform, source_url=source_url)
                fallback.steps.insert(
                    0,
                    AgentStep(
                        name="LLM fallback",
                        skill="prompts/full_job_analysis.md + qwen",
                        status="failed",
                        summary=f"LLM analysis failed and the agent fell back to rule-based analysis: {exc}",
                        evidence=[],
                        output={},
                    ),
                )
                return fallback

        return self._run_rule_pipeline(raw_text, source_platform=source_platform, source_url=source_url)

    def run_from_url(
        self,
        url: str,
        source_platform: str = "",
        prefer_llm: bool = True,
    ) -> AgentRunResult:
        fetched = self.fetcher(url)
        run = self.run(
            fetched.text,
            source_platform=source_platform,
            source_url=url,
            prefer_llm=prefer_llm,
        )
        run.steps.insert(
            0,
            AgentStep(
                name="Fetch job page",
                skill="web_fetcher",
                summary="Fetched the job page and extracted readable text.",
                evidence=[item for item in [fetched.title, fetched.url] if item],
                output={
                    "url": fetched.url,
                    "title": fetched.title,
                    "text_preview": fetched.text[:300],
                },
            ),
        )
        return run

    def _run_rule_pipeline(self, raw_text: str, source_platform: str = "", source_url: str = "") -> AgentRunResult:
        parsed_record = parse_job_text(raw_text, source_platform=source_platform, source_url=source_url)
        steps: list[AgentStep] = [self._build_extract_step(parsed_record)]

        haystack = " ".join(
            [
                parsed_record.job_title,
                parsed_record.jd_summary,
                " ".join(parsed_record.keywords),
                " ".join(parsed_record.skills),
                parsed_record.raw_text,
            ]
        ).lower()

        role_decision = analyze_role_category(haystack)
        steps.append(
            AgentStep(
                name="Classify role category",
                skill="skills/classify_role_category.md",
                summary=role_decision.reason,
                evidence=role_decision.evidence_keywords,
                output={
                    "role_category": role_decision.role_category,
                    "reason": role_decision.reason,
                    "evidence_keywords": role_decision.evidence_keywords,
                },
            )
        )

        match_decision = analyze_match_direction(haystack, role_decision.role_category)
        steps.append(
            AgentStep(
                name="Judge match direction",
                skill="skills/judge_match_direction.md",
                summary=match_decision.reason,
                evidence=[str(match_decision.match_score), match_decision.main_gap],
                output={
                    "match_direction": match_decision.match_direction,
                    "match_score": match_decision.match_score,
                    "reason": match_decision.reason,
                    "main_gap": match_decision.main_gap,
                },
            )
        )

        priority_decision = analyze_priority(haystack, match_decision)
        steps.append(
            AgentStep(
                name="Suggest priority",
                skill="skills/score_priority_and_resume_need.md",
                summary=priority_decision.short_note,
                evidence=priority_decision.resume_focus,
                output={
                    "priority": priority_decision.priority,
                    "custom_resume_needed": priority_decision.custom_resume_needed,
                    "resume_focus": priority_decision.resume_focus,
                    "short_note": priority_decision.short_note,
                },
            )
        )

        record = parsed_record.model_copy(
            update={
                "role_category": role_decision.role_category,
                "category_reason": role_decision.reason,
                "evidence_keywords": role_decision.evidence_keywords,
                "match_direction": match_decision.match_direction,
                "match_score": match_decision.match_score,
                "match_reason": match_decision.reason,
                "main_gap": match_decision.main_gap,
                "priority": priority_decision.priority,
                "recommend_resume_customization": priority_decision.custom_resume_needed,
                "resume_focus": priority_decision.resume_focus,
                "short_note": priority_decision.short_note,
            }
        )
        steps.append(self._build_review_step(record, "rules"))
        return AgentRunResult(record=record, steps=steps)

    def _build_extract_step(self, record: JobRecord) -> AgentStep:
        return AgentStep(
            name="Extract core fields",
            skill="skills/extract_job_fields.md",
            summary="Extracted baseline fields from the JD text for downstream decisions.",
            evidence=[item for item in [record.company, record.job_title, record.location] if item],
            output={
                "company": record.company,
                "job_title": record.job_title,
                "location": record.location,
                "is_internship": record.is_internship,
                "jd_summary": record.jd_summary,
                "keywords": record.keywords,
                "skills": record.skills,
                "education_requirement": record.education_requirement,
            },
        )

    def _build_review_step(self, record: JobRecord, mode: str) -> AgentStep:
        return AgentStep(
            name="Prepare human review",
            skill="review",
            summary="Prepared the final recommendation for human confirmation before writing to Excel.",
            evidence=[
                f"mode={mode}",
                f"priority={record.priority}",
                f"resume_customization={record.recommend_resume_customization}",
            ],
            output={
                "short_note": record.short_note,
                "resume_focus": record.resume_focus,
            },
        )
