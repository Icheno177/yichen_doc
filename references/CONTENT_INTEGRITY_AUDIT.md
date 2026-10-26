# Content Integrity Audit

## Extracted units

The current extractors support DOCX paragraphs/table cells, PDF page text/link annotations, PPTX text/table cells/images, XLSX populated cells/formulas/charts, HTML text/table/image/link references, and Markdown/text lines. Locators use page, slide, paragraph, table-cell, sheet-cell or source-line coordinates when available. IDs are deterministic for a file hash, locator and normalized text.

PDF text extraction may miss scanned/OCR-only content, figures, equations, or layout-specific reading order. PPTX text extraction does not prove chart-data fidelity or object visibility. Image registration is not image-equivalence verification. Record unsupported objects in a manual ledger.

## Matching and dispositions

Matching proceeds through exact text, normalized text, numeric/unit and direction tripwires, exact-substring/split candidates, then lexical candidates and human disposition. Allowed statuses: `RETAINED`, `REWRITTEN`, `MERGED`, `SPLIT`, `VISUALIZED`, `INTENTIONALLY_REMOVED`, `MISSING`, `CONFLICT`, and `UNRESOLVED`.

Authorized omissions need a reason and authorization. Visualizations need a destination locator and chart/data/source mapping. Similarity is only a review lead. Fixed-width 80-character windows are a separate compatibility metric; always state the denominator and method. Unit match rates and window match rates are not interchangeable.

Review headings, claims, table rows/cells, images/chart titles/data, equations, citations, footnotes, values/units, limitations, conclusions and recommendations. A numeric, negation or direction difference is a conflict candidate, not an automatic correction.
