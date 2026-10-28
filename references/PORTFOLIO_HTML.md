# Offline Research Portfolio HTML

Use this guide when a user requests a portfolio, multi-report showcase, research archive, or an offline HTML deliverable intended for review or sharing.

## 1. Establish the publication set

1. Search the named workspace and the specific adjacent folders the user identifies. Restrict the search to relevant document, slide, workbook, image, and source formats.
2. Inspect file contents and audit records. Do not select a "latest" version from its filename or modification time alone.
3. Record each considered deliverable's series, name, full source path, format, byte size, modification time, SHA-256, page/slide count where applicable, version/cutoff, audit state, desensitization state, and inclusion decision.
4. De-duplicate byte-identical files by SHA-256. Keep different versions when they contain distinct content; label their relationship and authority.
5. Treat explicit confidentiality, internal-use, or restricted-circulation markings as a publication block unless the user supplies valid authorization or an approved display copy. Do not embed a restricted source in Base64, a ZIP, hidden HTML data, or a preview image. Continue independent work and mark the affected series as restricted.
6. Include only display-approved files in a shareable portfolio. A filename containing "脱敏" does not establish that all embedded objects, notes, comments, metadata, images, or attachments have been sanitized; inspect the actual package and retain any unresolved status.

## 2. Preserve the full report

- Keep each report's original chapter order and text. Preserve headings, paragraphs, lists, native tables, merged cells where feasible, images, formulas, footnotes, citations, references, and appendices.
- Keep the overview separate from the full report. Never present an executive summary as the full-text report.
- Preserve the original wording inside the report. Apply first-person voice only to newly written portfolio introductions and project summaries when requested.
- Maintain separate evidence labels for facts, internal data, assumptions, calculations, judgments, and recommendations. Keep the original evidence state and audit state; do not upgrade an estimate or a blocked review to a verified result.
- For desensitized materials, preserve `████` consistently. A mask means withheld/redacted, not zero and not proof that the underlying value is unknown. Keep source-status details in a private ledger, outside the display bundle.
- If a requested complete report cannot be published because the only source is restricted, explain the restriction in the portfolio and mark the report unavailable. Do not paraphrase or reconstruct restricted content into a hidden or nominally safe download.

## 3. Build a truly offline single-file HTML

- Embed CSS, JavaScript, approved images, charts, logo, and slide-preview images. Do not use CDN scripts, web fonts, local server dependencies, or absolute local file paths.
- Use semantic sections, readable typography, responsive layouts, keyboard-operable controls, descriptive alt text, and a clear report/section navigation path.
- Provide global search over the included text and direct links among home, report sections, slide viewer, downloads, and portfolio notes.
- A slide viewer should preserve aspect ratio and order, show current page count, support previous/next and thumbnail navigation, and allow a larger view without cropping the original slide.
- Use a real approved brand asset. Preserve its aspect ratio, brand colors, and negative space. If transparency conversion is necessary, retain internal white logo details and record source, method, dimensions, alpha-channel check, and visual edge review.
- Minimize image payloads only with non-destructive or visually verified transformations. Do not downsample full-slide previews below legibility when a larger view is promised.

## 4. Embed downloadable deliverables safely

- Embed only display-approved originals. Preserve original DOCX/PPTX/XLSX/PDF bytes; do not rewrite or recompress Office packages.
- For each download, record the original SHA-256 and byte size in the local source manifest. Reconstruct the embedded payload independently from the finished HTML and compare its SHA-256 to the source before claiming byte-identical downloads.
- Use safe display filenames and Blob/local-browser download behavior. Never put an absolute local path in a resource URL or visible HTML data. Keep full source paths only in the separate local manifest when needed for traceability.
- If total attachment size may cause browser memory or download problems, measure the output. Keep the primary HTML complete; add a verified ZIP fallback when needed and document exactly which files were embedded or placed in the fallback.
- Do not create a download button for a file that is missing, restricted, or not embedded. State its actual availability and reason.

## 5. Record audit state and version relationships

For each series, state the selected full-text source, the presentation version, the data workbook version, the version cutoff, and the relationship among them. Clearly mark historical and superseded files.

Use specific statuses such as `audited`, `partial review`, `working draft`, `not independently verified`, `restricted`, or `not included`. Do not use `PASS`, `complete`, or `zero loss` beyond the scope supported by the underlying evidence. A file opening, text extraction, slide count, candidate phrase match, or successful download proves only that narrow check.

## 6. Final checks

- Parse the finished HTML and verify that its CSS/JS and images are embedded, its resource references contain no local absolute paths, and it opens as a `file://` document without network access.
- Compare the manifest to the actual source set, record page/slide counts and hashes, and verify all payloads by independent extraction and hashing.
- Search the HTML and embedded-text layer for restricted identifiers, unmasked values, placeholder language, stale metrics, and contradictory version claims. Inspect the actual source notes/comments/hidden sheets where relevant.
- Open the finished file in a browser. Check responsive behavior, navigation, search, slide changes, image enlargement, and one download per format. Confirm downloaded bytes against the source hash.
- Report unresolved authorization, visual, content, or browser limits plainly. Do not describe a partial portfolio as containing all reports or all deliverables.
