"""Utilities for fetching and cleaning web page text."""

from __future__ import annotations

import re
from dataclasses import dataclass
from html import unescape
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)


@dataclass
class WebFetchResult:
    url: str
    title: str
    text: str


class WebFetchError(RuntimeError):
    """Raised when a job page cannot be fetched or parsed."""


def fetch_job_page_text(url: str, timeout: int = 12) -> WebFetchResult:
    request = Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urlopen(request, timeout=timeout) as response:
            body = response.read()
            charset = response.headers.get_content_charset() or "utf-8"
    except HTTPError as exc:
        raise WebFetchError(f"HTTP {exc.code}") from exc
    except URLError as exc:
        raise WebFetchError(f"Network error: {exc.reason}") from exc
    except Exception as exc:  # pragma: no cover
        raise WebFetchError(str(exc)) from exc

    html = body.decode(charset, errors="ignore")
    title = extract_title(html)
    text = extract_visible_text(html)
    if not text:
        raise WebFetchError("The page did not contain readable text.")
    return WebFetchResult(url=url, title=title, text=text)


def extract_title(html: str) -> str:
    match = re.search(r"<title[^>]*>(.*?)</title>", html, flags=re.IGNORECASE | re.DOTALL)
    if not match:
        return ""
    return normalize_whitespace(strip_tags(match.group(1)))


def extract_visible_text(html: str) -> str:
    cleaned = re.sub(r"(?is)<script.*?>.*?</script>", " ", html)
    cleaned = re.sub(r"(?is)<style.*?>.*?</style>", " ", cleaned)
    cleaned = re.sub(r"(?is)<noscript.*?>.*?</noscript>", " ", cleaned)
    cleaned = re.sub(r"(?i)</p>|</div>|</li>|</tr>|<br\\s*/?>|</h[1-6]>", "\n", cleaned)
    cleaned = strip_tags(cleaned)
    cleaned = unescape(cleaned)
    cleaned = normalize_whitespace(cleaned)
    return cleaned


def strip_tags(html: str) -> str:
    return re.sub(r"(?s)<[^>]+>", " ", html)


def normalize_whitespace(text: str) -> str:
    text = text.replace("\r", "\n")
    text = re.sub(r"[ \t\f\v]+", " ", text)
    text = re.sub(r"\n\s*", "\n", text)
    text = re.sub(r"\n{2,}", "\n", text)
    return text.strip()
