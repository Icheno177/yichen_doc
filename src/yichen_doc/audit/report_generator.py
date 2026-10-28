"""Write reproducible machine-readable and reviewer-facing audit outputs."""
from __future__ import annotations

import csv
from pathlib import Path
from .schemas import jsonable, write_json


def write_csv(path: Path, rows: list[dict], columns: list[str] | None = None) -> None:
    if columns is None:
        columns = list(rows[0]) if rows else []
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def write_reports(out: Path, *, summary: dict, mappings: list[dict], claims: dict, model: dict,
                  conflicts: dict, issues: list[dict], manifest: dict, remediation: list[str]) -> None:
    out.mkdir(parents=True, exist_ok=True)
    write_json(out / "audit_summary.json", summary)
    write_csv(out / "content_mapping.csv", mappings)
    write_json(out / "content_mapping.json", mappings)
    write_csv(out / "claim_evidence_ledger.csv", claims.get("ledger", []))
    write_json(out / "model_audit.json", model)
    write_json(out / "qa_conflicts.json", conflicts)
    write_csv(out / "issues.csv", issues)
    write_json(out / "audit_manifest.json", manifest)
    (out / "remediation_plan.md").write_text("# Remediation plan\n\n" + "\n".join(f"{i}. {item}" for i, item in enumerate(remediation, 1)) + "\n", encoding="utf-8")
    lines = ["# Audit summary", "", f"**Overall status: {summary.get('overall_status', 'BLOCKED')}**", "",
             "| Check | Scope | Denominator | Result | Status |", "|---|---|---:|---:|---|"]
    for check in summary.get("checks", []):
        metric = check.get("output_metric", {})
        lines.append(f"| {check.get('check_id')} {check.get('check_name')} | {check.get('input_scope')} | {check.get('denominator')} | {metric} | {check.get('status')} |")
    lines += ["", "## Limitations", ""]
    lines.extend(f"- {x}" for x in summary.get("limitations", []))
    lines += ["", "## Open issues", ""]
    lines.extend(f"- **{x.get('severity')} {x.get('issue_id')}** — {x.get('description')}" for x in issues)
    (out / "audit_summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
