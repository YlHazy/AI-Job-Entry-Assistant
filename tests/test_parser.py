from src.parser import parse_job_text


def test_parse_job_text_extracts_core_fields() -> None:
    raw_text = """
    公司：星河智能科技
    岗位名称：AI Agent 开发实习生
    工作地点：上海
    岗位职责：
    负责基于 Python、RAG、LLM 和工作流搭建智能助手。
    任职要求：
    本科及以上，熟悉 Prompt Engineering、OpenAI API、LangChain。
    """

    record = parse_job_text(raw_text, source_platform="实习僧", source_url="https://example.com/job")

    assert record.company == "星河智能科技"
    assert record.job_title == "AI Agent 开发实习生"
    assert record.location == "上海"
    assert record.is_internship is True
    assert record.education_requirement == "本科及以上"
    assert "Python" in record.skills
    assert "LLM" in record.keywords
