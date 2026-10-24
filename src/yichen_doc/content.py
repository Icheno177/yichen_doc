"""Load, validate, and cross-check the shared research content contract."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

EVIDENCE_TYPES = {"FACT", "INTERNAL DATA", "ASSUMPTION", "CALCULATION", "JUDGMENT", "RECOMMENDATION"}
BLOCK_TYPES = {"paragraph", "heading", "table", "chart", "metric", "callout", "image", "citation", "formula"}


def load_content(path: str | Path) -> dict[str, Any]:
    source = Path(path)
    data = json.loads(source.read_text(encoding="utf-8"))
    validate_content(data, source.parent)
    return data


def validate_content(data: dict[str, Any], base_dir: Path | None = None) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        raise ValueError("Root must be a JSON object")
    for key in ("schema_version", "metadata", "decision", "sources", "sections"):
        if key not in data:
            errors.append(f"Missing required field: {key}")
    if data.get("schema_version") != "1.0":
        errors.append("schema_version must be 1.0")
    metadata = data.get("metadata", {})
    for key in ("title", "date", "language"):
        if not metadata.get(key):
            errors.append(f"metadata.{key} is required")
    if base_dir:
        for key in ("logo_path", "cover_image_path"):
            if metadata.get(key) and not (base_dir / metadata[key]).resolve().is_file():
                errors.append(f"metadata.{key} image file not found: {metadata[key]}")
    decision = data.get("decision", {})
    for key in ("question", "answer"):
        if not decision.get(key):
            errors.append(f"decision.{key} is required")
    sources = data.get("sources", [])
    source_ids = [x.get("id") for x in sources if isinstance(x, dict)]
    if len(source_ids) != len(set(source_ids)):
        errors.append("source ids must be unique")
    ids = set(source_ids)
    metric_ids: set[str] = set()
    for metric in data.get("metrics", []):
        if metric.get("id") in metric_ids:
            errors.append(f"duplicate metric id: {metric.get('id')}")
        metric_ids.add(metric.get("id"))
        if metric.get("source_id") and metric["source_id"] not in ids:
            errors.append(f"metric {metric.get('id')} references unknown source_id")
        if metric.get("evidence_type") and metric["evidence_type"] not in EVIDENCE_TYPES:
            errors.append(f"metric {metric.get('id')} has invalid evidence_type")
    for ci, calculation in enumerate(data.get("calculations", [])):
        for input_id in calculation.get("input_ids", []):
            if input_id not in metric_ids:
                errors.append(f"calculations[{ci}] references unknown input metric: {input_id}")
        for source_id in calculation.get("source_ids", []):
            if source_id not in ids:
                errors.append(f"calculations[{ci}] references unknown source id: {source_id}")
        output_id = calculation.get("output_metric_id")
        if output_id and output_id not in metric_ids:
            errors.append(f"calculations[{ci}] references unknown output metric: {output_id}")
        excel_formula = calculation.get("excel_formula")
        if excel_formula and not excel_formula.startswith("="):
            errors.append(f"calculations[{ci}].excel_formula must start with '='")
    section_ids: set[str] = set()
    for si, section in enumerate(data.get("sections", [])):
        sid = section.get("id")
        if not sid or sid in section_ids:
            errors.append(f"sections[{si}].id must be present and unique")
        section_ids.add(sid)
        for bi, block in enumerate(section.get("blocks", [])):
            where = f"sections[{si}].blocks[{bi}]"
            kind = block.get("type")
            if kind not in BLOCK_TYPES:
                errors.append(f"{where}.type is invalid: {kind}")
                continue
            for source_id in block.get("source_ids", []):
                if source_id not in ids:
                    errors.append(f"{where} references unknown source id: {source_id}")
            if kind == "table":
                headers = block.get("headers", [])
                if not headers or any(len(row) != len(headers) for row in block.get("rows", [])):
                    errors.append(f"{where} table rows must match non-empty headers")
            if kind == "chart":
                cats = block.get("categories", [])
                if not cats or not block.get("series"):
                    errors.append(f"{where} chart needs categories and series")
                if kind == "chart" and block.get("chart_type") == "scatter":
                    xs = block.get("x_values", [])
                    if len(xs) != len(cats):
                        errors.append(f"{where} scatter chart needs one numeric x_value per category")
                if kind == "chart" and block.get("chart_type") == "pie" and len(block.get("series", [])) != 1:
                    errors.append(f"{where} pie chart must have exactly one series")
                for series in block.get("series", []):
                    if len(series.get("values", [])) != len(cats):
                        errors.append(f"{where} chart series length must match categories")
            if kind == "image" and base_dir and block.get("image_path"):
                image_path = (base_dir / block["image_path"]).resolve()
                if not image_path.is_file():
                    errors.append(f"{where} image file not found: {block['image_path']}")
    if errors:
        raise ValueError("Content contract failed:\n- " + "\n- ".join(errors))
    return errors
