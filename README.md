# yichen_doc

**Evidence-led research and four-format document production.** `yichen_doc` keeps research content separate from its DOCX, PPTX, XLSX, and HTML renderers. Build one source-backed content package, select the required output formats, and keep the resulting documents editable. Every rendered deliverable visibly carries the signature **出版人：谢翊忱**; Office file metadata uses 谢翊忱 as creator where supported.

## What it does

- Preserves the existing research and writing policy: evidence grading, source traceability, assumption and calculation labels, direct professional language, resume truthfulness, and accurate AI terminology.
- Provides a shared, versioned JSON content contract for decisions, sections, sources, metrics, assumptions, tables, charts, and images.
- Renders DOCX with Word headings, an automatic table-of-contents field, source list, page fields, editable tables, and embedded figures.
- Renders PPTX with PptxGenJS, native editable text, tables, and charts.
- Renders XLSX with README, Sources, Inputs, Calculations, Scenarios, Sensitivity, Dashboard, and QA sheets.
- Renders HTML with responsive styling, section navigation, sortable/filterable table text, source links, charts, and print styles.
- Validates content references, units and series lengths, package structure, and build outputs.
- Adds a separate Audit Engine V2 for staged content mapping, evidence/model ledgers, package checks, QA conflict reconciliation, and rendered-page review.

The system name and repository remain `yichen_doc`. Four-format support does not mean every task must generate four deliverables.

## Install and run

From the repository root:

```powershell
python -m pip install -e .
npm install
yichen_doc validate examples/sample_research.json
yichen_doc build examples/sample_research.json --formats docx,pptx,xlsx,html --out outputs
```

To generate only one or two formats, pass just those formats. You can also use `python -m yichen_doc` instead of the installed command. The sample is clearly marked as fictional and serves as a renderer demonstration.

Install optional audit-format readers when needed: `python -m pip install -e ".[audit]"`. HTML browser checks additionally need an installed Playwright Chromium browser; without it, browser rendering is reported `BLOCKED`.

## Audit existing deliverables

Create a private JSON manifest listing the original source, revised document and final presentation, plus optional claim/model ledgers and rendered pages. Then run:

```powershell
yichen_doc audit audit_manifest.json --out audit_outputs
```

The engine keeps source→revision, revision→presentation, evidence→claim, model inputs→outputs, and file→rendered pages as separate checks. It writes a source-unit mapping, issue register, check registry, model/evidence outputs, QA reconciliation and remediation plan. Similarity candidates are not proof of retention. Windows PowerPoint can render slides when available; pages stay `REVIEW_REQUIRED` until a named reviewer signs each page.

Keep private manifests, reports, source files, model inputs and renders outside public commits. See [QUALITY_ASSURANCE.md](references/QUALITY_ASSURANCE.md), [CONTENT_INTEGRITY_AUDIT.md](references/CONTENT_INTEGRITY_AUDIT.md), [EVIDENCE_AUDIT.md](references/EVIDENCE_AUDIT.md), [MODEL_AUDIT.md](references/MODEL_AUDIT.md), [VISUAL_AUDIT.md](references/VISUAL_AUDIT.md), and [AUDIT_ACCEPTANCE.md](references/AUDIT_ACCEPTANCE.md).

## Architecture

| Layer | Responsibility |
| --- | --- |
| Research | Question framing, evidence ledger, source checks, calculations |
| Content | Decision, conclusions, sections, blocks, citations, metadata |
| Data contract | Metric values, units, periods, source IDs, assumptions, formulas |
| Renderers | Independent DOCX, PPTX, XLSX, HTML generation |
| QA | Contract validation, package checks, formulas, citations, visual rendering |

Details: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md), [schema](src/yichen_doc/schema/research_content.schema.json), [mapping and inventory](docs/UPGRADE_INVENTORY.md).

## Skill use

Use [SKILL.md](SKILL.md) and [references/WRITING_POLICY.md](references/WRITING_POLICY.md) for routing, research workflow, evidence rules, and output selection. The examples remain fictional and contain no personal career facts or confidential client data. The repository-level [AGENTS.md](AGENTS.md) applies these rules to work in this checkout.

## Golden Sets and templates

`golden_sets/word/` and `golden_sets/powerpoint/` contain style-only manifests. Private source names, paths, fingerprints, content, and brand assets are excluded. `templates/docx/` and `templates/pptx/` contain editable generic production templates.

## Tests and verification

```powershell
python -m unittest discover -s tests -v
python -m pytest -q
```

The test suite validates the shared contract, source references, renderer structure, editable native objects, formulas, and document links. Visual output still needs review in its real reader: open Word, PowerPoint, Excel, and a browser; render all presentation pages and inspect the contact sheet. An artifact existing or passing a structural test does not prove final visual quality.

Audit outcomes are `PASS`, `PASS_WITH_WARNINGS`, `FAIL`, or `BLOCKED`. Missing ledgers, unresolved mappings, unavailable rendering, or missing human approvals prevent a full `PASS`.

## License

MIT. See [LICENSE](LICENSE).
