"""Output-level QA for generated Office and HTML artifacts."""
from __future__ import annotations

import json
import zipfile
from pathlib import Path


def inspect_output(path: str | Path, expected_kind: str | None = None) -> dict:
    p = Path(path)
    if not p.is_file() or p.stat().st_size == 0:
        raise ValueError(f"Output missing or empty: {p}")
    result = {"path": str(p), "bytes": p.stat().st_size, "kind": expected_kind or p.suffix.lstrip(".")}
    if p.suffix.lower() in {".docx", ".pptx", ".xlsx"}:
        with zipfile.ZipFile(p) as z:
            bad = z.testzip()
            if bad:
                raise ValueError(f"Corrupt package member: {bad}")
            names = set(z.namelist())
            if p.suffix.lower() == ".docx" and "word/document.xml" not in names:
                raise ValueError("DOCX package has no document.xml")
            if p.suffix.lower() == ".pptx" and "ppt/presentation.xml" not in names:
                raise ValueError("PPTX package has no presentation.xml")
            if p.suffix.lower() == ".xlsx" and "xl/workbook.xml" not in names:
                raise ValueError("XLSX package has no workbook.xml")
            result["package_members"] = len(names)
    elif p.suffix.lower() == ".html":
        body = p.read_text(encoding="utf-8")
        for token in ("<!doctype html>", "</html>"):
            if token not in body.lower():
                raise ValueError(f"HTML missing required boundary {token}")
        result["has_script"] = "<script" in body.lower()
    return result


def write_qa_report(items: list[dict], path: str | Path) -> None:
    Path(path).write_text(json.dumps({"status": "PASS", "artifacts": items}, ensure_ascii=False, indent=2), encoding="utf-8")
