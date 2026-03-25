from src.web_fetcher import extract_title, extract_visible_text


def test_extract_visible_text_removes_script_and_keeps_content() -> None:
    html = """
    <html>
      <head><title>岗位详情</title><style>.x{color:red;}</style></head>
      <body>
        <script>console.log('ignore')</script>
        <div>公司：星河智能科技</div>
        <p>岗位名称：AI Agent 开发实习生</p>
        <p>负责 Python、RAG 和 Agent 工作流。</p>
      </body>
    </html>
    """

    text = extract_visible_text(html)
    assert "console.log" not in text
    assert "公司：星河智能科技" in text
    assert "岗位名称：AI Agent 开发实习生" in text


def test_extract_title_returns_page_title() -> None:
    assert extract_title("<html><head><title>岗位详情页</title></head></html>") == "岗位详情页"
