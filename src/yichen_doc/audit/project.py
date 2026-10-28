"""Run staged, non-substitutable audits from a local manifest."""
from __future__ import annotations

import json
from pathlib import Path
from .conflict_detection import reconcile_checks
from .engine import audit_transition
from .format_audits import audit_docx, audit_html, audit_xlsx
from .issue_registry import CHECK_REGISTRY_VERSION
from .report_generator import write_csv
from .render import render_pptx
from .schemas import write_json
from .visual_audit import audit_rendered_pages


def _resolve(base: Path, value):
    if not value: return None
    p = Path(value)
    return p if p.is_absolute() else base / p


def run_project(manifest_path: str | Path, out_dir: str | Path) -> dict:
    manifest_path = Path(manifest_path).resolve()
    base, out = manifest_path.parent, Path(out_dir).resolve()
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    audit_run_id = __import__("datetime").datetime.now().strftime("%Y%m%dT%H%M%S")
    reports = data.get("reports") or [data]
    all_stage_results, all_issues, checks, legacy_unmatched_windows = [], [], [], []
    for report in reports:
        name = report.get("name", "report")
        source = _resolve(base, report.get("source"))
        revised = _resolve(base, report.get("revised"))
        presentation = _resolve(base, report.get("presentation"))
        claims = _resolve(base, report.get("claims"))
        models = _resolve(base, report.get("models"))
        visual_dir = _resolve(base, report.get("rendered_pages"))
        review_file = _resolve(base, report.get("visual_review"))
        mapping_review_file = _resolve(base, report.get("mapping_review"))
        stages = []
        if source and revised:
            stages.append(("source_to_revised", source, revised, None))
        if revised and presentation:
            render_result = None
            if report.get("render_presentation") and presentation.suffix.lower() == ".pptx":
                visual_dir = out / name / "rendered_pages" / audit_run_id
                render_result = render_pptx(presentation, visual_dir)
            stages.append(("revised_to_presentation", revised, presentation, visual_dir))
        else:
            render_result = None
        if source and presentation:
            stages.append(("source_to_presentation_direct", source, presentation, None))
        report_results = []
        for stage, left, right, rendered in stages:
            target_dir = out / name / stage
            result = audit_transition(left, right, target_dir, claims_path=claims if stage == "revised_to_presentation" else None,
                                      models_path=models if stage == "revised_to_presentation" else None,
                                      rendered_pages=rendered, review_file=review_file,
                                      mapping_review_path=mapping_review_file,
                                      verify_urls=bool(data.get("verify_urls", False)), pipeline_stage=stage)
            report_results.append(result)
            all_issues.extend(result["issues"])
            checks.extend(result["summary"]["checks"])
            if stage == "revised_to_presentation":
                window_map = target_dir / "document_window_mapping.json"
                if window_map.is_file():
                    legacy_unmatched_windows.extend({"report": name, **row} for row in json.loads(window_map.read_text(encoding="utf-8"))
                                                     if row.get("mapping_status") == "UNRESOLVED")
        format_results = []
        for key in ("docx", "xlsx", "html"):
            path = _resolve(base, report.get(key))
            if not path: continue
            if key == "docx":
                res = audit_docx(path, _resolve(base, data.get("word_golden_set")))
            elif key == "xlsx": res = audit_xlsx(path)
            else: res = audit_html(path, browser_check=bool(data.get("browser_check", False)),
                                   screenshot_path=out / name / "html_audit" / "page.png" if data.get("browser_check") else None)
            format_results.append({"format": key, "file": str(path.resolve()), "result": res})
            write_json(out / name / f"{key}_audit.json", res)
        all_stage_results.append({"report": name, "stages": report_results, "format_audits": format_results, "render_result": render_result})
    prior = data.get("prior_checks", [])
    conflicts = reconcile_checks(prior)
    # A difference between distinct stages/denominators is documented as
    # non-comparable; only same-key/same-scope disagreement blocks a pass.
    unresolved_maps = sum(s["mapping_stats"]["unresolved_unit_count"] for rep in all_stage_results for s in rep["stages"])
    has_required_inputs = all(rep.get("stages") for rep in all_stage_results) and bool(data.get("acceptance_ledgers_provided", False))
    overall = "FAIL" if any(x.get("severity") in {"CRITICAL", "HIGH"} for x in all_issues) else "BLOCKED" if unresolved_maps or not has_required_inputs or conflicts["conflicts"] else "PASS_WITH_WARNINGS"
    summary = {"overall_status": overall, "audit_engine": "V2", "report_count": len(all_stage_results), "stage_results": all_stage_results,
               "mapping_unresolved_count": unresolved_maps, "qa_conflict_reconciliation": conflicts,
               "legacy_unmatched_document_windows": len(legacy_unmatched_windows),
               "checks_registry": [{"check_id": x["check_id"], "check_name": x["check_name"], "status": x["status"], "input_scope": x["input_scope"], "denominator": x["denominator"]} for x in checks],
               "limitations": ["Each source→revision, revision→presentation and direct source→presentation check has a separate scope.", "Missing ledgers or reviewer records prevent a PASS even when text checks succeed.", "Every target page requires a reviewer disposition; rendered images do not count as human approval."]}
    out.mkdir(parents=True, exist_ok=True)
    write_json(out / "audit_summary.json", summary)
    write_json(out / "qa_conflicts.json", conflicts)
    write_csv(out / "issues.csv", all_issues)
    write_csv(out / "legacy_window_unmatched.csv", legacy_unmatched_windows)
    write_json(out / "legacy_window_unmatched.json", legacy_unmatched_windows)
    flat = []
    for rep in all_stage_results:
        for st in rep["stages"]:
            flat.extend(st["summary"]["checks"])
    write_csv(out / "check_registry.csv", flat)
    remediation = ["Review each source unit whose destination is missing, conflicting or only a lexical candidate.",
                   "Provide structured claim-evidence and model-input ledgers; preserve unknown values as missing.",
                   "Render every target page and record page-by-page human approval, separately from automatic checks.",
                   "Resolve same-scope QA conflicts; document non-comparable metrics with their distinct scope and denominator."]
    (out / "remediation_plan.md").write_text("# Remediation plan\n\n" + "\n".join(f"{i}. {v}" for i, v in enumerate(remediation, 1)) + "\n", encoding="utf-8")
    stage_manifests = []
    for report in all_stage_results:
        for stage in report["stages"]:
            stage_manifest = Path(stage["output_dir"]) / "audit_manifest.json"
            if stage_manifest.is_file():
                stage_manifests.append(json.loads(stage_manifest.read_text(encoding="utf-8")))
    input_files = {x["path"]: x for m in stage_manifests for x in m.get("input_files", [])}
    audit_manifest = {"audit_time_utc": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(),
                      "tool": "yichen_doc Audit Engine V2", "checks_registry_version": CHECK_REGISTRY_VERSION,
                      "manifest": str(manifest_path), "scope": data.get("scope", "user-provided report pairs"),
                      "input_files": list(input_files.values()),
                      "checks_executed": sorted({x["check_id"] for x in checks if x.get("status") != "NOT_RUN"}),
                      "checks_not_run": sorted({x["check_id"] for x in checks if x.get("status") == "NOT_RUN"} |
                                               {check_id for m in stage_manifests for check_id in m.get("checks_not_run", [])}),
                      "private_manifest_not_copied": True}
    write_json(out / "audit_manifest.json", audit_manifest)
    legacy_lines = ["| Report | Stage | Exact windows | Denominator | Hit rate | Unmatched |", "|---|---|---:|---:|---:|---:|"]
    for report_result in all_stage_results:
        for stage_result in report_result["stages"]:
            stats = stage_result["mapping_stats"].get("legacy_document_wide_window_screen", {})
            legacy_lines.append(f"| {report_result['report']} | {stage_result['summary']['stage']} | {stats.get('exact_matches', 0)} | {stats.get('denominator', 0)} | {stats.get('exact_match_rate')} | {stats.get('denominator', 0) - stats.get('exact_matches', 0)} |")
    (out / "audit_summary.md").write_text("# Audit Engine V2 summary\n\n**Overall status: " + overall + "**\n\n" +
        "This report keeps source completeness, revised-to-presentation mapping, evidence, calculations, file structure, QA reconciliation, and rendered-page review as separate checks.\n\n"+
        f"Reports: {len(all_stage_results)}; mapping units needing disposition: {unresolved_maps}; legacy document windows without exact text hits: {len(legacy_unmatched_windows)}; same-scope QA conflicts: {len(conflicts['conflicts'])}.\n\n"+
        "## Document-wide 80-character screen by stage\n\n" + "\n".join(legacy_lines) + "\n\n"+
        "The historical 59/350 and 26/83 figures belong to revised Markdown → PPT text screening. They do not measure original-source completeness. The per-item unmatched windows are in `legacy_window_unmatched.csv` and `.json`.\n\n"+
        "A missing ledger, unresolved content mapping, or missing human visual approval blocks PASS. See `issues.csv`, per-stage `content_mapping.csv`, `check_registry.csv`, and `remediation_plan.md`.\n", encoding="utf-8")
    test_dir = out / "test_results"
    test_dir.mkdir(parents=True, exist_ok=True)
    write_json(test_dir / "audit_run_smoke.json", {"status": "PASS" if all_stage_results else "FAIL",
               "stage_count": sum(len(x["stages"]) for x in all_stage_results),
               "report_count": len(all_stage_results), "audit_exit_status": overall,
               "meaning": "The audit command completed and produced stage reports; this is not a content-completeness or visual-acceptance result."})
    return {"overall_status": overall, "output_dir": str(out), "reports": len(all_stage_results), "unresolved_maps": unresolved_maps, "issues": len(all_issues)}
