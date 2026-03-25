from pathlib import Path

from openpyxl import load_workbook

from src.excel_writer import append_job_record
from src.schemas import JobRecord


def test_append_job_record_creates_workbook_and_sheet(tmp_path: Path) -> None:
    excel_path = tmp_path / "jobs.xlsx"
    record = JobRecord(
        company="星河智能科技",
        job_title="AI Agent 开发实习生",
        role_category="开发",
        match_direction="AI Agent 开发",
        priority="高",
        recommend_resume_customization="是",
        location="上海",
        source_platform="实习僧",
    )

    append_job_record(excel_path, record)

    workbook = load_workbook(excel_path)
    worksheet = workbook["JobBoard"]
    assert worksheet["B2"].value == "星河智能科技"
    assert worksheet["C2"].value == "AI Agent 开发实习生"
    assert worksheet["D2"].value == "开发"
