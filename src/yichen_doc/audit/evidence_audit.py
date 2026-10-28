"""Claim-to-evidence checks for explicitly supplied claim ledgers."""
from __future__ import annotations

from urllib.parse import urlparse

VALID_LABELS = {"FACT", "INTERNAL_DATA", "ASSUMPTION", "CALCULATION", "JUDGMENT", "RECOMMENDATION"}
VALID_GRADES = {"A", "B", "C", "D", "E"}


def audit_claims(claims: list[dict], sources: list[dict], *, check_urls: bool = False, timeout: float = 6.0) -> dict:
    by_id = {str(s.get("source_id", s.get("id", ""))): s for s in sources}
    rows, issues = [], []
    for index, claim in enumerate(claims, 1):
        cid = str(claim.get("claim_id", f"CLAIM-{index:04d}"))
        label = str(claim.get("label", "")).upper()
        refs = [str(x) for x in claim.get("evidence_ids", claim.get("source_ids", []))]
        linked = [by_id[x] for x in refs if x in by_id]
        missing = [x for x in refs if x not in by_id]
        if label not in VALID_LABELS:
            issues.append({"issue_id": f"EVID-{cid}", "severity": "HIGH" if claim.get("critical") else "MEDIUM", "category": "evidence", "locator": claim.get("locator", ""), "description": "Claim has no recognized evidence label.", "status": "OPEN"})
        if not refs and label not in {"ASSUMPTION", "JUDGMENT", "RECOMMENDATION"}:
            issues.append({"issue_id": f"EVID-SOURCE-{cid}", "severity": "HIGH" if claim.get("critical") else "MEDIUM", "category": "evidence", "locator": claim.get("locator", ""), "description": "Claim lacks a linked source or model input.", "status": "OPEN"})
        for source_id in missing:
            issues.append({"issue_id": f"EVID-MISSING-{cid}-{source_id}", "severity": "HIGH", "category": "evidence", "locator": claim.get("locator", ""), "description": f"Unknown evidence ID: {source_id}", "status": "OPEN"})
        for source in linked:
            grade = str(source.get("grade", "")).upper()
            if grade not in VALID_GRADES:
                issues.append({"issue_id": f"EVID-GRADE-{cid}-{source.get('id')}", "severity": "MEDIUM", "category": "evidence", "locator": claim.get("locator", ""), "description": "Source grade is missing or invalid.", "status": "OPEN"})
            if check_urls:
                url = source.get("url", "")
                result = _verify_url(url, timeout) if url else "MISSING_URL"
            else:
                result = "UNVERIFIED" if source.get("url") else "NOT_APPLICABLE"
        rows.append({
            "claim_id": cid, "claim_text": claim.get("claim_text", claim.get("text", "")),
            "claim_location": claim.get("locator", claim.get("claim_location", "")), "label": label,
            "evidence_ids": refs, "source_titles": [s.get("title", "") for s in linked],
            "publishers": [s.get("publisher", s.get("organization", "")) for s in linked],
            "publication_dates": [s.get("publication_date", s.get("date", "")) for s in linked],
            "reporting_periods": [s.get("reporting_period", s.get("period", "")) for s in linked],
            "source_urls": [s.get("url", "") for s in linked], "evidence_grades": [s.get("grade", "") for s in linked],
            "data_definition": claim.get("data_definition", ""), "unit": claim.get("unit", ""),
            "limitations": claim.get("limitations", ""),
            "verification_status": "UNVERIFIED" if linked and not check_urls else ("LINKED" if linked else "MISSING")
        })
    return {"claim_count": len(rows), "ledger": rows, "issues": issues,
            "external_urls_checked": check_urls,
            "limitations": ["Claim extraction is not inferred automatically; supply claims in the audit manifest.", "A reachable URL does not prove that it supports the claim."]}


def _verify_url(url: str, timeout: float) -> str:
    try:
        import urllib.request
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"}:
            return "INVALID_SCHEME"
        request = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "yichen_doc-audit/2"})
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return "URL_REACHABLE" if 200 <= response.status < 400 else f"HTTP_{response.status}"
    except Exception as exc:
        return f"UNVERIFIED:{type(exc).__name__}"
