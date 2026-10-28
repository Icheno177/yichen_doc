"""Reconcile QA metrics by scope and denominator before judging conflicts."""
from __future__ import annotations


def reconcile_checks(checks: list[dict]) -> dict:
    groups: dict[tuple, list[dict]] = {}
    for check in checks:
        key = (check.get("check_id"), check.get("input_scope"), check.get("denominator"), check.get("method"), check.get("version"))
        groups.setdefault(key, []).append(check)
    reconciled, conflicts = [], []
    for key, rows in groups.items():
        values = [r.get("value") for r in rows]
        same = len(set(map(str, values))) <= 1
        record = {"check_id": key[0], "input_scope": key[1], "denominator": key[2], "method": key[3], "version": key[4], "values": values,
                  "status": "CONSISTENT" if same else "CONFLICT"}
        reconciled.append(record)
        if not same:
            conflicts.append({**record, "issue_id": f"QA-CONFLICT-{len(conflicts)+1:03d}", "severity": "HIGH", "description": "Same QA check key reports different results."})
    # Surface different denominators/methods as non-comparable rather than a conflict.
    by_name: dict[str, list[dict]] = {}
    for check in checks: by_name.setdefault(check.get("check_name", check.get("check_id", "")), []).append(check)
    non_comparable = []
    for name, rows in by_name.items():
        keys = {(r.get("input_scope"), r.get("denominator"), r.get("method"), r.get("version")) for r in rows}
        if len(keys) > 1:
            non_comparable.append({"check_name": name, "variants": [dict(input_scope=r.get("input_scope"), denominator=r.get("denominator"), method=r.get("method"), version=r.get("version"), value=r.get("value")) for r in rows], "status": "NON_COMPARABLE_UNTIL_SCOPE_ALIGNED"})
    return {"checks": reconciled, "conflicts": conflicts, "non_comparable": non_comparable,
            "overall_conflict_status": "CONFLICTS_OPEN" if conflicts else "NO_SAME_SCOPE_CONFLICT"}
