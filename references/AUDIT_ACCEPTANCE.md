# Audit Acceptance Gate

## PASS

Require all of these: source/target files and hashes recorded; every material source unit has a reviewed destination or authorized disposition; no unresolved or conflicting critical units; claim-evidence links reviewed against supporting content; critical calculations independently reproduced with input classifications visible; QA scopes/methods/denominators/versions recorded and same-scope conflicts resolved; package checks pass; required pages have named human approval; sensitive inputs and outputs are excluded from public commits.

## PASS_WITH_WARNINGS

Use only when all acceptance gates are met and remaining lower-severity issues do not affect material content, evidence, calculation, usability or visual acceptance. Document each warning and its impact.

## FAIL and BLOCKED

- `FAIL`: confirmed CRITICAL/HIGH omission, contradiction, unsupported material claim, calculation error or package failure remains.
- `BLOCKED`: required files, structured claim/model ledgers, renderer or human review are missing; or source mapping remains unresolved.

Never grant PASS from a match-rate threshold. `REVIEW_REQUIRED`, `UNVERIFIED`, uncalculated formulas, or a different denominator are not approval.
