# Quality Assurance and Audit Engine V2

## When to audit

Run the engine when a user requests a quality audit, source-to-output completeness check, evidence/model verification, cross-format review, or page-level visual QA. Use scoped checks for narrow requests; do not trigger expensive full rendering for casual edits.

## Independent checks

| Check | Question answered | Does not prove |
|---|---|---|
| Source → revised | Where did each extracted source unit go? | That every paraphrase preserves meaning without review |
| Revised → presentation | Which revised units appear in slides? | That the revision preserved the original source |
| Evidence → claim | Are explicit claims linked to dated, graded sources? | That a reachable URL supports a claim |
| Model inputs → outputs | Can supported formulas be recalculated from classified inputs? | That unverified assumptions are business results |
| File → rendered pages | Can pages be rendered, indexed and reviewed? | Human readability/correctness without named review |
| XLSX/HTML | What formulas, errors, resources and structures exist? | Arbitrary spreadsheet recalc or browser compatibility without a real run |

## Status meanings

- `PASS`: required checks pass, no unresolved critical/high issue, and required human sign-off exists.
- `PASS_WITH_WARNINGS`: acceptance requirements are met with lower-severity findings documented.
- `FAIL`: a confirmed critical/high issue remains.
- `BLOCKED`: required source, ledger, renderer, or human review evidence is absent.

Similarity candidates, `UNVERIFIED`, and `REVIEW_REQUIRED` never mean verified retention. See [AUDIT_ACCEPTANCE.md](AUDIT_ACCEPTANCE.md).
