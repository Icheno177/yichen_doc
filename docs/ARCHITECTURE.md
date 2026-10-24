# yichen_doc 2.0 architecture

`yichen_doc` is organized around one source-backed research content package and separate output engines. Renderers format the content; they do not verify or rewrite evidence.

## Five layers

| Layer | Inputs | Outputs | Responsibility |
| --- | --- | --- | --- |
| Research | User question, permitted sources, internal data | Evidence ledger, scope, open gaps | Frame the decision; identify primary sources and limitations; calculate only supportable metrics |
| Content | Evidence and calculations | Typed sections and blocks | Draft conclusions, narrative, tables, charts, assumptions, risks, recommendations |
| Data contract | Content and source ledger | Versioned JSON | Store metric ID, value, unit, period, evidence type, formula, source ID, and metadata |
| Renderers | Validated contract | DOCX, PPTX, XLSX, HTML | Generate each requested output independently while preserving facts and formulas |
| QA | Contract and generated files | Pass/fail results and visual review | Check references, calculations, package structure, editability, layout, and rendering |

The JSON schema is in `src/yichen_doc/schema/`. Runtime validation is implemented in `content.py`. Calculations can include a readable formula and a corresponding Excel formula; unknown inputs remain empty. Chart series carry category labels, unit, type, and source identifiers.

## Renderer responsibilities

- DOCX uses `python-docx` plus OOXML for document fields, headings, tables, citations, and page fields. Optional cover/logo images are supplied through metadata paths; the engine does not fabricate company branding or silently invent cover art.
- PPTX uses PptxGenJS. Tables and charts remain native PowerPoint objects; image blocks are individual replaceable image objects.
- XLSX uses `openpyxl` and includes the standard research sheets. Calculations carry live formulas; charts reference the workbook's own data cells.
- HTML uses semantic headings and tables, responsive CSS, section navigation, source links, hover-labelled charts, table filtering/sorting, a light/dark toggle, and browser print styles.

The sample research package is fictional. It demonstrates source links, an assumption-labelled metric, a formula and a chart. It is not evidence about a real company or market.

## Installation and QA lifecycle

1. `python -m pip install -e .` installs the Python command `yichen_doc`.
2. `npm install` installs the PptxGenJS dependency.
3. `yichen_doc validate <content.json>` checks required fields, IDs, references, table shapes, chart lengths, and local image paths.
4. `yichen_doc build <content.json> --formats ... --out ...` renders selected formats and writes a QA JSON record.
5. `python -m unittest discover -s tests -v` exercises the contract and all four renderers.
6. Open final files in their real readers; render all PPTX slides, check the contact sheet, and confirm formula and TOC recalculation in Office. Automated package checks cannot establish visual acceptance.

## Design choices and boundaries

- No provider account, remote data API, or private source is needed by the engine.
- Golden source documents are not embedded in the package. Only style manifests and blank templates are included.
- HTML charts and XLSX/PPTX charts use the same content series. DOCX preserves chart data as an editable table until a native document-chart workflow is added.
- No renderer invents missing sources, financial parameters, output values, medical claims, or decision thresholds.
- The JSON contract does not remove the need for evidence review or a human decision owner.
