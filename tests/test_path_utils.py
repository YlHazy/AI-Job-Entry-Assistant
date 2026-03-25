from src.path_utils import normalize_sheet_name, normalize_user_text


def test_normalize_user_text_strips_quotes() -> None:
    assert normalize_user_text('"C:\\Users\\foo\\岗位看板.xlsx"') == r"C:\Users\foo\岗位看板.xlsx"
    assert normalize_user_text("'JobBoard'") == "JobBoard"


def test_normalize_sheet_name_supports_quoted_input() -> None:
    assert normalize_sheet_name('"JobBoard"') == "JobBoard"
