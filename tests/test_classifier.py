from src.classifier import enrich_job_record
from src.schemas import JobRecord


def test_enrich_job_record_marks_agent_role_high_priority() -> None:
    record = JobRecord(
        job_title="AI Agent 开发实习生",
        jd_summary="负责 Agent workflow、RAG、LLM 应用开发和 Python 后端能力建设。",
        keywords=["LLM", "RAG", "工作流"],
        skills=["Python", "OpenAI", "LangChain"],
        raw_text="需要负责 Agent、RAG、Prompt、Python 开发。",
    )

    enriched = enrich_job_record(record)

    assert enriched.role_category == "开发"
    assert enriched.match_direction == "AI Agent 开发"
    assert enriched.priority == "高"
    assert enriched.recommend_resume_customization == "是"
