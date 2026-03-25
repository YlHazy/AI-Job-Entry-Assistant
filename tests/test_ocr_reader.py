from PIL import Image

from src.ocr_reader import OCRUnavailableError, extract_text_from_image_bytes


def test_extract_text_from_image_bytes_raises_when_backend_missing(monkeypatch, tmp_path) -> None:
    image_path = tmp_path / "sample.png"
    Image.new("RGB", (20, 20), color="white").save(image_path)
    image_bytes = image_path.read_bytes()

    import builtins

    real_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name == "pytesseract":
            raise ModuleNotFoundError("missing pytesseract")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)

    try:
        try:
            extract_text_from_image_bytes(image_bytes, backend="pytesseract")
        except OCRUnavailableError as exc:
            assert "pytesseract is not installed" in str(exc)
        else:
            raise AssertionError("Expected OCRUnavailableError")
    finally:
        monkeypatch.setattr(builtins, "__import__", real_import)
