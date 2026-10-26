from __future__ import annotations

from pathlib import Path
from ._common import add


def extract_text(path: Path):
    units = []
    section = ""
    for i, raw in enumerate(path.read_text(encoding="utf-8-sig", errors="replace").splitlines(), 1):
        text = raw.strip()
        if not text:
            continue
        kind = "heading" if text.startswith("#") else ("table_row" if text.startswith("|") else "paragraph")
        if kind == "heading": section = text.lstrip("# ")
        item = add(path, f"line[{i:06d}]", kind, text, section)
        if item: units.append(item)
    return units
