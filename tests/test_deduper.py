from src.deduper import looks_like_duplicate
from src.schemas import JobRecord


def test_looks_like_duplicate_detects_same_url() -> None:
    record = JobRecord(company="星河智能科技", job_title="AI Agent 开发实习生", source_url="https://example.com/job")
    history = [{"id": 7, "company": "星河智能科技", "job_title": "AI Agent 开发实习生", "source_url": "https://example.com/job"}]

    result = looks_like_duplicate(record, history)

    assert result.is_duplicate is True
    assert result.reason == "来源链接重复"
    assert result.matched_id == 7


def test_looks_like_duplicate_detects_same_company_and_title() -> None:
    record = JobRecord(company="星河智能科技", job_title="AI Agent 开发实习生")
    history = [{"id": 8, "company": "星河智能科技", "job_title": "AI Agent 开发实习生", "source_url": ""}]

    result = looks_like_duplicate(record, history)

    assert result.is_duplicate is True
    assert result.reason == "公司和岗位名称重复"


def test_looks_like_duplicate_detects_similar_titles() -> None:
    record = JobRecord(company="星河智能科技", job_title="AI Agent 开发实习")
    history = [{"id": 9, "company": "星河智能科技", "job_title": "AI Agent 开发实习生", "source_url": ""}]

    result = looks_like_duplicate(record, history)

    assert result.is_duplicate is True
    assert result.reason == "公司和岗位名称高度相似"
    assert result.similarity > 0.85
