"""Stable issue/check IDs and conservative overall acceptance."""
from __future__ import annotations

CHECKS = {
    "QA-001": "Source to revised-document completeness",
    "QA-002": "Revised document to presentation mapping",
    "QA-003": "Claim and evidence traceability",
    "QA-004": "Independent model recalculation and input quality",
    "QA-005": "Rendered-page visual review",
    "QA-006": "Cross-format consistency",
    "QA-007": "QA metric scope and conflict reconciliation",
    "QA-008": "File structure and package integrity",
}
CHECK_REGISTRY_VERSION = "2.0.0"


def overall_status(*, issues: list[dict], mapping_unresolved: int, evidence_configured: bool,
                   model_configured: bool, visual_pages: list[dict], conflicts: list[dict],
                   required_files_present: bool = True) -> str:
    if any(x.get("severity") == "CRITICAL" and x.get("status", "OPEN") not in {"FIXED", "VERIFIED", "WAIVED"} for x in issues):
        return "FAIL"
    if any(x.get("severity") == "HIGH" and x.get("status", "OPEN") not in {"FIXED", "VERIFIED", "WAIVED"} for x in issues):
        return "FAIL"
    if not required_files_present or mapping_unresolved or not evidence_configured or not model_configured or not visual_pages:
        return "BLOCKED"
    if conflicts or any(x.get("status") in {"REVIEW_REQUIRED", "AUTO_WARNING", "AUTO_FAIL"} for x in visual_pages):
        return "BLOCKED"
    if any(x.get("status") != "HUMAN_APPROVED" for x in visual_pages):
        return "BLOCKED"
    return "PASS_WITH_WARNINGS" if issues else "PASS"
