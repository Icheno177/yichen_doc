# Incremental upgrade inventory and rule mapping

## Starting repository state

The source checkout was clean at start. Branch and HEAD were recorded before edits; the isolated branch is `codex/yichen-doc-2.0-upgrade`, based on `d7b12e4917b01e0951b9ff41a2d0e92e3731574e`. The existing installed copy matched the source files before work. The installed copy was synchronized after verification; generated outputs and dependency folders were excluded.

## Existing function inventory

| Existing item | Existing purpose | 2.0 treatment |
| --- | --- | --- |
| `SKILL.md` | Skill trigger, research workflow, evidence and writing safeguards | Preserved and updated with renderer selection and command-line production flow |
| `README.md` | Installation, usage, policy overview, limitations | Preserved; expanded with contract, renderers, QA and examples |
| `references/WRITING_POLICY.md` | Evidence, thesis, research, style, resume and technical rules | Preserved and integrated into data labels and renderer guidance |
| `references/ANTI_AI_WRITING.md` | Natural-language and phrase safeguards | Retained and linked from the Skill |
| `references/STYLE_SPEC.md` | Style and tone rules | Retained and linked from the Skill |
| `references/EVIDENCE_RULES.md` | Source grading and claim handling | Retained and linked from the Skill |
| `references/RESEARCH_WORKFLOW.md` | Research sequence and source logging | Retained and linked from the Skill |
| `references/REPORT_PATTERNS.md` | Industry, diligence, and business-case patterns | Retained and linked from the Skill |
| `references/QUANTITATIVE_METHODS.md` | Formulas, forecasting and scenario methods | Retained and wired into shared metric/calculation fields |
| `examples/*.md` | Anonymized writing examples | Retained; JSON sample added to exercise production engines |
| `tests/*.md`, `tests/test_policy_regressions.py` | Static acceptance cases and policy regressions | Retained relevant cases, removed obsolete integration cases, added contract and end-to-end tests |
| `agents/openai.yaml` | Codex-facing display metadata and implicit invocation | Retained with concise four-format prompt |

## Original rule to production mapping

| Original rule | Engine or test implementation |
| --- | --- |
| Source quality, traceability, contradictions | `WRITING_POLICY.md`; `source.grade`, source metadata, source IDs; contract checks |
| Facts versus assumptions and calculations | Metric `evidence_type`; calculation inputs, readable formulas, Excel formulas |
| Do not invent missing data | Blank `value` support; formula guards; QA descriptions; end-to-end formula tests |
| Professional natural writing | `SKILL.md`, `WRITING_POLICY.md`, existing style references and writing cases |
| Quantitative methods and sensitivity | Calculation and assumption structures; XLSX Inputs/Calculations/Scenarios/Sensitivity |
| Presentation readability and editability | Native PptxGenJS text, tables, charts; editable template; rendered visual review process |
| Long-form DOCX structure | DOCX template with cover, TOC field, heading hierarchy, source section and page field |
| Spreadsheet model and dashboard | Eight standardized workbook sheets; formula and chart support |
| Interactive/printable HTML | Navigation, client-side table filtering/sorting, hover values, responsive styles, theme toggle and print CSS |
| Do not force every output format | Explicit CLI `--formats` selector and Skill guidance |

## Golden Set evidence

The requested exact Word file name was not found. The previously recovered redacted source document was used only for style statistics; its text, tables, data, and images were not copied into the repository. The supplied 48-slide PowerPoint reference was located and analyzed for canvas, shapes, fonts, colors, pictures, tables, and positions. See the two audit notes under `golden_sets/`.

## Exclusions and privacy

No remote repository changes, push, publication, source report copying, or Golden Set overwrite occurred. The golden originals remain in their original user locations. The produced templates use placeholders and contain no company report content or private branding assets.
