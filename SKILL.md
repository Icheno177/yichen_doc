---
name: yichen-doc
description: Research, analyze, and produce evidence-led deliverables for external readers. Use when work needs a report, presentation, workbook, dashboard, or formal document that another person may rely on. Preserve traceable facts, assumptions, calculations, and clear decisions; casual explanations and creative writing do not need this Skill unless requested.
metadata:
  short-description: Evidence-led research and four-format production
---

# yichen_doc

`yichen_doc` is a research content system and document production toolkit. It supports a shared research content model rendered independently as DOCX, PPTX, XLSX, and HTML. Select only the output formats the user needs.

## Use the writing rules

Apply [references/WRITING_POLICY.md](references/WRITING_POLICY.md) first. It preserves evidence grading, research logic, natural writing, career safeguards, and technical terminology rules. Use only the route-specific guidance needed for the task:

- Industry, company, due diligence, and business case: [references/REPORT_PATTERNS.md](references/REPORT_PATTERNS.md)
- Evidence records and source quality: [references/EVIDENCE_RULES.md](references/EVIDENCE_RULES.md)
- Research sequence and source log: [references/RESEARCH_WORKFLOW.md](references/RESEARCH_WORKFLOW.md)
- Forecasts, unit economics, and sensitivity: [references/QUANTITATIVE_METHODS.md](references/QUANTITATIVE_METHODS.md)
- Style and anti-template language: [references/STYLE_SPEC.md](references/STYLE_SPEC.md), [references/ANTI_AI_WRITING.md](references/ANTI_AI_WRITING.md)

## Production architecture

Keep research facts, content, data definitions, renderers, and QA separate. A shared JSON contract lives at `src/yichen_doc/schema/research_content.schema.json` and is implemented by `src/yichen_doc/content.py`.

1. Research and evidence ledger establish claims, sources, dates, limits, and open questions.
2. Content records decision question, answer, metrics, assumptions, risks, recommendations, sections, and typed blocks.
3. Data fields preserve value, unit, time period, evidence type, formula, and source identifiers.
4. Independent renderers create DOCX, native editable PPTX, XLSX, and HTML. They consume the same content file and can be selected individually.
5. QA validates the content contract, artifact package structure, source references, formulas, and visual rendering where an office renderer is available.

Never fabricate missing inputs. Keep unknown values blank and state why they are missing. A renderer does not upgrade the source quality of its content.

### Desensitized showcase outputs

When the user requests a desensitized presentation, report, workbook, or web showcase, use a consistent visible mask such as `████` for undisclosed values, identities, records, or evidence. Treat a mask as **withheld/redacted**, never as zero or as proof that a value is unknown. Preserve the underlying source and evidence status in the private source package and traceability ledger; do not alter originals. Keep masked fields consistent across prose, charts, tables, formulas, notes, and exports. A calculation depending on a masked input must remain masked or be shown only as an explicitly labelled partial expression. Never infer a complete ROI, NPV, deployment result, or other outcome from masked inputs.

### Research portfolio websites

When producing an offline portfolio or multi-report showcase, read [PORTFOLIO_HTML.md](references/PORTFOLIO_HTML.md). The guide covers source selection, display authorization, complete report conversion, slide preview, embedded downloads, integrity checks, and offline/browser QA. A portfolio card or executive summary does not substitute for the complete report when full reading is requested.

### Python charts and slide annotations

For research presentations with quantitative evidence, create charts with Python from a traceable data table or model. Choose chart types that fit the evidence (for example lines for scenario changes, waterfall for additive bridges, donut for a reconciled composition, heatmaps for sensitivity, and funnel for conversion stages); use multiple types when the source data supports them, without inventing a time series or forcing decorative chart variety. Every chart needs a visible annotation stating the decision-relevant reading, unit and period, source/model basis, and material assumption or limitation. Keep chart notes attached to their chart in every exported format. Prefer editable PowerPoint chart or shape objects when practical.

## Audit existing or generated deliverables

Use `yichen_doc audit <audit_manifest.json> --out <audit_outputs>` when the user requests a quality audit, source-to-output completeness review, evidence/model verification, cross-format comparison, or page-level visual QA. Do not run expensive full audits automatically for casual tasks or simple edits.

Keep these checks separate: original source → revised document; revised document → presentation; evidence → claim; model inputs → calculations → outputs; and file → rendered pages plus human visual review. Exact text, normalized text, numeric/conflict checks, lexical candidates, merge/split candidates, and visualized items are different dispositions. Similarity is a review lead, not proof. Record scope, method, denominator, input hashes, limitations, and unrun checks.

Missing mappings, unresolved critical evidence/model findings, unresolved same-scope QA conflicts, absent renderings, or missing human page approvals must prevent a full `PASS`. See [references/QUALITY_ASSURANCE.md](references/QUALITY_ASSURANCE.md) and [references/AUDIT_ACCEPTANCE.md](references/AUDIT_ACCEPTANCE.md).

Current limits: claim extraction requires an explicit claim ledger; URL reachability does not prove claim support; arbitrary Excel formulas are inventoried but not recalculated; machine rendering never means human visual approval. See the audit references for format-specific coverage.

## Generate deliverables

Install Python dependencies and Node dependencies from the repository root, then run:

```powershell
python -m pip install -e .
npm install
yichen_doc validate examples/sample_research.json
yichen_doc build examples/sample_research.json --formats docx,pptx,xlsx,html --out outputs
```

Choose the requested formats, for example `--formats docx` or `--formats pptx,html`. Python users can also call `python -m yichen_doc`. The JSON contract is the renderer input; renderers do not independently change claims or calculations.

### Publisher attribution

Every rendered research deliverable must visibly include the exact signature **“出版人：谢翊忱”**. Apply it to DOCX page footers, every PPTX slide (including the cover), the XLSX workbook front sheet and print footers, and the HTML page footer. Set Office document creator metadata to 谢翊忱 where supported. Preserve the signature when exporting DOCX/PPTX to PDF. Do not add or alter this attribution in user-provided source files; it belongs to yichen_doc-generated outputs.

For a quality check, run `python -m unittest discover -s tests -v` and inspect generated files in Word/PowerPoint/Excel and a browser. For PPTX, render every page and review the full contact sheet; structural checks do not replace visual review.

## Writing workflow

1. Frame the decision, reader, deadline, scope, and consequence of error.
2. Build an evidence ledger with claim, evidence type, source, source grade, date, limitation, and unresolved conflict.
3. Calculate only decision-relevant quantities and preserve units, formulas, and inputs.
4. Draft the conclusion from the evidence and calculations.
5. Identify material risks, mitigations, triggers, and decision owners.
6. Run the evidence-quality review for unsupported claims, hidden assumptions, contradictions, and unowned recommendations.
7. Render only the requested formats and run content, structural, quantitative, and visual checks appropriate to those outputs.

Recommendations identify action, owner, timeline, resource, KPI, and stop/go condition where source evidence supports them.

## Preserved safeguards

- Separate FACT, INTERNAL DATA, ASSUMPTION, CALCULATION, JUDGMENT, and RECOMMENDATION when the distinction affects a decision.
- Grade material evidence A–E. Critical claims require strong support; do not treat low-grade material as proof.
- Do not infer a business result from financing, registered capital, user counts, a benchmark, or correlation alone.
- Disclose material contradictions and limitations. Do not add weak objections solely for appearance.
- Resumes do not invent titles, employers, degrees, project status, revenue, ROI, training, launches, or adoption.
- Distinguish models, prompts, retrieval, knowledge bases, rules, workflows, tool use, agents, human review, evaluation, and data pipelines.
- Avoid empty narration, defensive phrasing, unsupported hedging, promotional claims, and fabricated precision.

## Limits

`yichen_doc` structures evidence and generates editable artifacts. It cannot create missing evidence, replace professional judgment, or guarantee a business outcome. The available sources, permitted internal data, and installed office renderers determine what can be verified.
