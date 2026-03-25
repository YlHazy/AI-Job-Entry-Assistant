"""OCR helpers for screenshot-based job intake."""

from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO

from PIL import Image

from src.config import OCR_BACKEND


class OCRUnavailableError(RuntimeError):
    """Raised when the configured OCR backend is unavailable."""


@dataclass
class OCRResult:
    text: str
    backend: str


def extract_text_from_image_bytes(image_bytes: bytes, backend: str = OCR_BACKEND) -> OCRResult:
    image = Image.open(BytesIO(image_bytes))
    image.load()

    if backend == "pytesseract":
        return _run_pytesseract(image)

    raise OCRUnavailableError(f"Unsupported OCR backend: {backend}")


def _run_pytesseract(image: Image.Image) -> OCRResult:
    try:
        import pytesseract
    except ModuleNotFoundError as exc:
        raise OCRUnavailableError(
            "pytesseract is not installed. Install `pytesseract` and a local Tesseract engine to enable OCR input."
        ) from exc

    text = pytesseract.image_to_string(image, lang="chi_sim+eng").strip()
    if not text:
        raise OCRUnavailableError("OCR completed but did not extract readable text from the image.")
    return OCRResult(text=text, backend="pytesseract")
