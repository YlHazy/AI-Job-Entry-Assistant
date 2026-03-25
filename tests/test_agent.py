from src.agent import JobIntakeAgent


def test_job_intake_agent_returns_trace_and_record() -> None:
    agent = JobIntakeAgent()
    raw_text = """
    公司：星河智能科技
    岗位名称：AI Agent 开发实习生
    工作地点：上海
    负责基于 Python、RAG、LLM、Prompt 和工作流搭建智能助手。
    本科及以上，熟悉 API 集成和 Agent workflow。
    """

    result = agent.run(raw_text, source_platform="实习僧", source_url="https://example.com/job", prefer_llm=False)

    assert result.record.company == "星河智能科技"
    assert result.record.role_category == "开发"
    assert result.record.match_direction == "AI Agent 开发"
    assert result.record.priority == "高"
    assert len(result.steps) == 5
    assert result.steps[0].name == "Extract core fields"
    assert result.steps[-1].name == "Prepare human review"
