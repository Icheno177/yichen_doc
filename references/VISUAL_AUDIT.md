# Rendered-Page Visual Audit

On Windows with PowerPoint installed, the engine can export one 1600×900 PNG per slide. It records preview paths, page numbers, dimensions and basic blank/low-resolution screening. It does not infer shape positions, overflow, chart sources, editability, logo compliance, or factual correctness from pixels alone.

Pages start at `REVIEW_REQUIRED` unless an obvious technical issue produces `AUTO_WARNING` or `AUTO_FAIL`. A named reviewer and timestamp must be supplied for each approved page; rendering success never means human approval.

DOCX Golden Set checks currently compare section geometry and paragraph-style usage only. Word pagination, headers/footers and clipping need a true Word render. XLSX structure checks do not recalculate arbitrary formulas. HTML resource checks do not guarantee browser compatibility; optional Playwright is needed for page load, console and screenshot checks. PDF extraction is not visual review; supply rendered page images.

```json
{"pages":[{"page":1,"reviewer":"Reviewer name","reviewed_at":"2026-10-26T10:00:00+08:00","approved":true,"notes":"Readable; no clipping."}]}
```

Approval must exist for every page. Contact sheets are navigation aids; inspect each page at readable scale.
