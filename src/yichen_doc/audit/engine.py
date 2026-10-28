"""Independent audit runner for source→revision and revision→presentation."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

from .. import __version__
from .content_mapping import apply_mapping_review, map_document_windows, map_units, mapping_stats
from .conflict_detection import reconcile_checks
from .cross_format_audit import audit_files, parity_check
from .evidence_audit import audit_claims
from .extractors import extract
from .issue_registry import CHECKS, CHECK_REGISTRY_VERSION, overall_status
from .model_audit import audit_models
from .report_generator import write_csv, write_reports
from .schemas import CheckRecord, MappingStatus, sha256_file, write_json
from .visual_audit import audit_rendered_pages


def _git_revision() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL, text=True).strip()
    except Exception:
        return "UNKNOWN"


def audit_transition(source_path: str | Path, target_path: str | Path, out_dir: str | Path, *,
                     claims_path: str | Path | None = None, models_path: str | Path | None = None,
                     rendered_pages: str | Path | None = None, review_file: str | Path | None = None,
                     mapping_review_path: str | Path | None = None, verify_urls: bool = False,
                     pipeline_stage: str = "source_to_target") -> dict:
    source_path, target_path, out = Path(source_path), Path(target_path), Path(out_dir)
    if not source_path.is_file() or not target_path.is_file():
        raise FileNotFoundError(f"Required audit file missing: source={source_path.is_file()} target={target_path.is_file()}")
    source_units, target_units = extract(source_path), extract(target_path)
    mappings = map_units(source_units, target_units)
    if mapping_review_path and Path(mapping_review_path).is_file():
        mappings = apply_mapping_review(mappings, str(mapping_review_path))
    stats = mapping_stats(mappings, source_units, target_units)
    document_windows = map_document_windows(source_units, target_units, stats["fixed_window_width"])
    issues = []
    for r in mappings:
        if r.mapping_status == MappingStatus.MISSING:
            issues.append({"issue_id": "MAP-" + r.source_unit_id, "severity": "HIGH", "category": "content_mapping", "file": r.source_file, "locator": r.source_locator, "description": "Source content unit has no target candidate.", "evidence": r.source_text[:500], "expected": "Mapped destination or authorized omission", "actual": "No destination", "proposed_fix": "Locate and map, restore, or record an authorized removal.", "status": "OPEN"})
        elif r.mapping_status == MappingStatus.CONFLICT:
            issues.append({"issue_id": "CONFLICT-" + r.source_unit_id, "severity": "CRITICAL", "category": "content_mapping", "file": r.target_file, "locator": r.target_locator, "description": r.notes, "evidence": r.source_text[:300], "expected": "Preserve numeric, direction and negation semantics", "actual": r.notes, "proposed_fix": "Review against original evidence and correct with a traceable change record.", "status": "OPEN"})
        elif r.mapping_status == MappingStatus.UNRESOLVED:
            issues.append({"issue_id": "REVIEW-" + r.source_unit_id, "severity": "MEDIUM", "category": "content_mapping", "file": r.source_file, "locator": r.source_locator, "description": "Lexical candidate requires human disposition; similarity is not proof.", "evidence": r.source_text[:300], "expected": "Verified mapping", "actual": r.target_locator, "proposed_fix": "Review candidate and mark retained, rewritten, merged, split, visualized, authorized removal, or missing.", "status": "OPEN"})
    sources, claims = [], []
    if claims_path and Path(claims_path).is_file():
        claim_data = json.loads(Path(claims_path).read_text(encoding="utf-8"))
        sources, claims = claim_data.get("sources", []), claim_data.get("claims", [])
    evidence = audit_claims(claims, sources, check_urls=verify_urls)
    issues.extend({**x, "category": "evidence", "file": str(claims_path or ""), "locator": x.get("locator", ""), "evidence": x.get("description", ""), "expected": "Claim linked to sufficient evidence", "actual": x.get("description", ""), "proposed_fix": "Complete the claim-evidence record and review whether source supports the claim.", "owner": "Research owner"} for x in evidence["issues"])
    models = []
    if models_path and Path(models_path).is_file():
        model_data = json.loads(Path(models_path).read_text(encoding="utf-8"))
        models = model_data.get("models", [])
    model_result = audit_models(models)
    issues.extend({**x, "category": "model", "file": str(models_path or ""), "locator": x.get("issue_id", ""), "evidence": x.get("description", ""), "expected": "Model inputs classified and recalculation reconciled", "actual": x.get("description", ""), "proposed_fix": "Supply missing evidence or correct the calculation/model definition.", "owner": "Model owner"} for x in model_result["issues"])
    visual = {"page_count": 0, "pages": [], "human_approved": 0, "status": "BLOCKED", "reason": "No rendered images supplied; no human visual approval recorded."}
    if rendered_pages:
        visual = audit_rendered_pages(rendered_pages, out / "visual_audit", review_file=review_file)
    file_audit = audit_files([source_path, target_path])
    issues.extend({**x, "category": "structure", "expected": "Readable file structure", "actual": x.get("description", ""), "proposed_fix": "Repair the file package and rerun extraction.", "owner": "Document owner"} for x in file_audit["issues"])
    checks = [
        CheckRecord("QA-001" if pipeline_stage == "source_to_revised" else "QA-002", CHECKS["QA-001" if pipeline_stage == "source_to_revised" else "QA-002"], "Map every source unit to its target disposition", f"{source_path.name} → {target_path.name}", "Exact → normalized → numbers/entities/direction → lexical review candidate", f"{len(source_units)} extracted source units; fixed-width {stats['fixed_window_width']} char windows={stats['window_denominator']}", {"window_exact_matches": stats["exact_window_matches"], "window_exact_rate": stats["exact_window_match_rate"], "unit_status_counts": stats["unit_status_counts"]}, [stats["interpretation"]], "BLOCKED" if stats["unresolved_unit_count"] else "REVIEW_REQUIRED"),
        CheckRecord("QA-006", CHECKS["QA-006"], "Check file package and extracted-unit parity", f"{source_path.suffix} → {target_path.suffix}", "Format extractor + exact-unit search", "all extracted source units", parity_check(source_units, target_units), file_audit["limitations"], "PASS_WITH_WARNINGS"),
        CheckRecord("QA-003", CHECKS["QA-003"], "Link material claims to dated, graded sources", "Explicit claims ledger only", "Claim/source ID validation; optional URL reachability", f"{len(claims)} supplied claims", {"claim_count": len(claims), "unlinked_claims": sum(x.get("verification_status") == "MISSING" for x in evidence.get("ledger", []))}, evidence["limitations"], "NOT_RUN" if not (claims_path and Path(claims_path).is_file()) else "PASS_WITH_WARNINGS"),
        CheckRecord("QA-004", CHECKS["QA-004"], "Independently recalculate key models", "Explicit model ledger only", "Safe arithmetic/ROI/NPV/IRR/payback evaluator", f"{len(models)} supplied models", {"model_count": len(models), "recalculated": sum(x["independent_output"] is not None for x in model_result["models"])}, model_result["limitations"], "NOT_RUN" if not (models_path and Path(models_path).is_file()) else "PASS_WITH_WARNINGS"),
        CheckRecord("QA-005", CHECKS["QA-005"], "Render page images and record machine/human state separately", str(rendered_pages or "none"), "Image dimensions/blank-page technical screen; explicit reviewer file", f"{visual.get('page_count', 0)} rendered pages", {"human_approved": visual.get("human_approved", 0), "page_count": visual.get("page_count", 0)}, ["Automated image checks cannot establish readability, clipping, source fidelity or correctness."], visual.get("status", "BLOCKED")),
        CheckRecord("QA-008", CHECKS["QA-008"], "Inspect file package structure", f"{source_path.name}, {target_path.name}", "Zip/package boundary and extractor success", "2 required input files", {"files": file_audit["files"]}, file_audit["limitations"], "FAIL" if file_audit["issues"] else "PASS"),
    ]
    qa_conflicts = reconcile_checks([])
    unresolved = stats["unresolved_unit_count"]
    status = overall_status(issues=issues, mapping_unresolved=unresolved, evidence_configured=bool(claims_path and Path(claims_path).is_file()), model_configured=bool(models_path and Path(models_path).is_file()), visual_pages=visual.get("pages", []), conflicts=qa_conflicts["conflicts"])
    summary = {"overall_status": status, "stage": pipeline_stage, "source_file": str(source_path.resolve()), "target_file": str(target_path.resolve()), "checks": [x.__dict__ for x in checks], "mapping_statistics": stats, "evidence_status": "CONFIGURED" if claims_path else "NOT_CONFIGURED", "model_status": "CONFIGURED" if models_path else "NOT_CONFIGURED", "visual_status": visual.get("status"), "issue_count": len(issues), "limitations": ["Unresolved mapping candidates block completeness PASS.", "Evidence and model claims are not inferred from document prose; provide structured ledgers.", "No HUMAN_APPROVED status is inferred from rendering or image inspection."]}
    manifest = {"audit_time_utc": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(), "tool": "yichen_doc Audit Engine V2", "tool_version": __version__, "checks_registry_version": CHECK_REGISTRY_VERSION, "git_commit": _git_revision(), "input_files": [{"path": str(p.resolve()), "sha256": sha256_file(p), "format": p.suffix.lower()} for p in [source_path, target_path]], "audit_scope": pipeline_stage, "checks_executed": [x.check_id for x in checks if x.status != "NOT_RUN"], "checks_not_run": [x.check_id for x in checks if x.status == "NOT_RUN"], "review_file": str(review_file) if review_file else "", "private_inputs_excluded_from_repo": True}
    remediation = [f"Resolve {stats['unresolved_unit_count']} source-unit mappings; do not treat lexical candidates as retained content.", "Supply explicit claim-evidence and model-input ledgers to enable those checks.", "Render every page and obtain named human review before visual acceptance."]
    write_reports(out, summary=summary, mappings=[x.__dict__ for x in mappings], claims=evidence, model=model_result, conflicts=qa_conflicts, issues=issues, manifest=manifest, remediation=remediation)
    write_csv(out / "document_window_mapping.csv", document_windows)
    write_json(out / "document_window_mapping.json", document_windows)
    return {"overall_status": status, "summary": summary, "mapping_stats": stats, "issues": issues, "output_dir": str(out.resolve())}
