"""Format-neutral structural checks plus strict parity ledgers."""
from __future__ import annotations

from pathlib import Path
from ..qa import inspect_output
from .extractors import extract
from .schemas import normalize


def audit_files(paths: list[str | Path]) -> dict:
    results, issues = [], []
    for path in paths:
        p = Path(path)
        try:
            package = inspect_output(p)
            units = extract(p)
            result = {"file": str(p.resolve()), "format": p.suffix.lower(), "status": "STRUCTURE_PASS", "unit_count": len(units), "package": package}
        except Exception as exc:
            result = {"file": str(p.resolve()), "format": p.suffix.lower(), "status": "FAIL", "error": f"{type(exc).__name__}: {exc}"}
            issues.append({"issue_id": f"STRUCT-{p.name}", "severity": "HIGH", "category": "structure", "file": str(p), "locator": "package", "description": result["error"], "status": "OPEN"})
        results.append(result)
    return {"files": results, "issues": issues, "limitations": ["Structure and extractability checks do not prove semantic completeness or visual readability."]}


def parity_check(reference_units, candidate_units) -> dict:
    candidate_text = "".join(normalize(x.text) for x in candidate_units)
    reference_count = matched = 0
    for unit in reference_units:
        n = normalize(unit.text)
        if not n: continue
        reference_count += 1
        matched += n in candidate_text
    return {"reference_unit_denominator": reference_count, "exact_units_found_in_candidate": matched,
            "exact_unit_rate": matched / reference_count if reference_count else None,
            "scope": "all extracted units in supplied reference and candidate files",
            "limitations": ["Exact text can be rearranged across target units; this is a screen, not a semantic judgment.", "A successful build does not prove data, image, chart or citation equivalence."]}
