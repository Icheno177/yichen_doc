# Operations and support

## Required runtimes

- Python 3.10 or later
- Node.js 18 or later
- Python packages installed by `pyproject.toml`
- PptxGenJS installed by `npm install`
- Microsoft Word, PowerPoint, Excel, LibreOffice, or compatible office software for final visual confirmation

## Commands

```powershell
python -m pip install -e .
npm install
yichen_doc validate examples/sample_research.json
yichen_doc build examples/sample_research.json --formats docx,pptx,xlsx,html --out outputs
python -m unittest discover -s tests -v
```

To refresh the style-only Golden Set from reference documents, pass their paths explicitly:

```powershell
python tools/extract_golden_sets.py --word "C:\path\to\reference.docx" --ppt "C:\path\to\reference.pptx"
```

Use a comma-separated subset in `--formats`. If a source image is referenced, store it relative to the JSON file and include its path and alt text. If inputs are unknown, leave metric values blank and explain the gap in the content or source limitation.

## Output QA

Every build writes a `*.qa.json` file. It confirms file existence and Office package structure. Tests verify editable native objects and expected formulas. Review DOCX pagination, field updates and TOC; PPTX every page and charts/tables; XLSX formulas and charts in an actual spreadsheet engine; HTML browser navigation, filtering, and print preview.

If PowerPoint is unavailable, PPTX content can still be structurally tested but the visual review status must remain pending. Do not describe unrendered output as visually accepted.
