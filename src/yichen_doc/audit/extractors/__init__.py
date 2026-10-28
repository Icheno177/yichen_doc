"""File-format extractors. Optional libraries are loaded only as needed."""
from __future__ import annotations

from pathlib import Path
from importlib import import_module

EXTRACTORS = {
    ".docx": ("docx", "extract_docx"), ".pdf": ("pdf", "extract_pdf"), ".pptx": ("pptx", "extract_pptx"),
    ".xlsx": ("xlsx", "extract_xlsx"), ".html": ("html", "extract_html"), ".htm": ("html", "extract_html"),
    ".md": ("text", "extract_text"), ".txt": ("text", "extract_text"), ".csv": ("text", "extract_text"),
}


def extract(path: str | Path) -> list[ContentUnit]:
    p = Path(path)
    try:
        module_name, function_name = EXTRACTORS[p.suffix.lower()]
    except KeyError as exc:
        raise ValueError(f"Unsupported audit input format: {p.suffix or '(no extension)'}") from exc
    try:
        extractor = getattr(import_module(f".{module_name}", __name__), function_name)
    except ImportError as exc:
        raise RuntimeError(f"Audit extractor for {p.suffix.lower()} needs an optional dependency: {exc}") from exc
    return extractor(p)
