from src.llm_analyzer import merge_payload_into_record, parse_json_content
from src.schemas import JobRecord


def test_parse_json_content_handles_markdown_fence() -> None:
    payload = parse_json_content(
        """```json
        {"company":"星河智能科技","job_title":"AI Agent 开发实习生"}
        ```"""
    )

    assert payload["company"] == "星河智能科技"
    assert payload["job_title"] == "AI Agent 开发实习生"


def test_merge_payload_into_record_falls_back_to_baseline() -> None:
    baseline = JobRecord(
        company="星河智能科技",
        job_title="AI Agent 开发实习生",
        location="上海",
        keywords=["LLM"],
        skills=["Python"],
        education_requirement="本科及以上",
        raw_text="sample",
    )

    record = merge_payload_into_record(
        baseline=baseline,
        payload={"job_title": "AI Agent 开发实习生", "priority": "high", "custom_resume_needed": "yes"},
        source_platform="实习僧",
        source_url="https://example.com/job",
        raw_text="sample",
    )

    assert record.company == "星河智能科技"
    assert record.priority == "高"
    assert record.recommend_resume_customization == "是"
    assert record.location == "上海"
