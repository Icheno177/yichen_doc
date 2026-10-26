"""Typed audit records and stable identifiers."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
import hashlib
import json
from pathlib import Path
from typing import Any


class MappingStatus(str, Enum):
    RETAINED = "RETAINED"
    REWRITTEN = "REWRITTEN"
    MERGED = "MERGED"
    SPLIT = "SPLIT"
    VISUALIZED = "VISUALIZED"
    INTENTIONALLY_REMOVED = "INTENTIONALLY_REMOVED"
    MISSING = "MISSING"
    CONFLICT = "CONFLICT"
    UNRESOLVED = "UNRESOLVED"

    def __str__(self) -> str:
        return self.value


class CheckStatus(str, Enum):
    PASS = "PASS"
    PASS_WITH_WARNINGS = "PASS_WITH_WARNINGS"
    FAIL = "FAIL"
    BLOCKED = "BLOCKED"
    NOT_RUN = "NOT_RUN"


@dataclass
class ContentUnit:
    unit_id: str
    file: str
    file_sha256: str
    locator: str
    section: str
    kind: str
    text: str
    numbers: list[str] = field(default_factory=list)
    citations: list[str] = field(default_factory=list)
    content_sha256: str = ""


@dataclass
class MappingRecord:
    source_unit_id: str
    source_file: str
    source_locator: str
    source_text: str
    target_file: str
    target_locator: str = ""
    target_unit_id: str = ""
    mapping_status: str = MappingStatus.UNRESOLVED
    match_method: str = ""
    similarity_score: float | None = None
    numeric_consistency: str = "NOT_CHECKED"
    citation_consistency: str = "NOT_CHECKED"
    reviewer_status: str = "REVIEW_REQUIRED"
    reviewer: str = ""
    reviewed_at: str = ""
    authorization: str = ""
    notes: str = ""


@dataclass
class AuditIssue:
    issue_id: str
    severity: str
    category: str
    file: str
    locator: str
    description: str
    evidence: str
    expected: str
    actual: str
    proposed_fix: str
    owner: str = "Research owner"
    status: str = "OPEN"


@dataclass
class CheckRecord:
    check_id: str
    check_name: str
    objective: str
    input_scope: str
    method: str
    denominator: str
    output_metric: dict[str, Any]
    limitations: list[str]
    status: str


def sha256_file(path: str | Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def unit_id(file_hash: str, locator: str, text: str) -> str:
    digest = hashlib.sha256((locator + "\0" + normalize(text)).encode("utf-8")).hexdigest()[:16]
    return f"U-{file_hash[:8]}-{digest}"


def normalize(text: str) -> str:
    return "".join(text.split()).replace("\u3000", "")


def jsonable(value: Any) -> Any:
    if hasattr(value, "value"):
        return value.value
    if hasattr(value, "__dataclass_fields__"):
        return {k: jsonable(v) for k, v in asdict(value).items()}
    if isinstance(value, dict):
        return {str(k): jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [jsonable(v) for v in value]
    return value


def write_json(path: str | Path, data: Any) -> None:
    Path(path).write_text(json.dumps(jsonable(data), ensure_ascii=False, indent=2), encoding="utf-8")
