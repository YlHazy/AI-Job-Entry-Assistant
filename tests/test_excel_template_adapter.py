from openpyxl import Workbook

from src.excel_template_adapter import detect_with_rules


def test_detect_with_rules_finds_header_row_and_columns() -> None:
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = "Board"
    worksheet["A1"] = "说明"
    headers = ["编号", "公司", "岗位名称", "岗位类别", "方向", "城市/办公形式", "JD链接", "来源渠道", "投递日期", "是否定制", "关键词命中度", "优先级", "当前状态", "风险/挂点", "复盘总结"]
    for idx, header in enumerate(headers, start=1):
        worksheet.cell(row=7, column=idx, value=header)

    mapping = detect_with_rules(worksheet, "test-key")

    assert mapping.header_row == 7
    assert mapping.data_start_row == 8
    assert mapping.key_columns["company"] == 2
    assert mapping.key_columns["job_title"] == 3
