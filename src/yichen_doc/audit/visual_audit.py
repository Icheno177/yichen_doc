"""Page image registration, technical screening and human review capture."""
from __future__ import annotations

import csv
from pathlib import Path
import shutil
from PIL import Image, ImageChops, ImageStat


def audit_rendered_pages(render_dir: str | Path, out_dir: str | Path, *, review_file: str | Path | None = None) -> dict:
    source = Path(render_dir)
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    candidates = sorted([*source.glob("*.png"), *source.glob("*.jpg"), *source.glob("*.jpeg")])
    approvals = {}
    if review_file and Path(review_file).is_file():
        import json
        approvals = {int(x["page"]): x for x in json.loads(Path(review_file).read_text(encoding="utf-8")).get("pages", [])
                     if x.get("reviewer") and x.get("reviewed_at") and x.get("approved") is True}
    rows, thumbs = [], []
    for index, image_path in enumerate(candidates, 1):
        with Image.open(image_path) as image:
            image = image.convert("RGB")
            width, height = image.size
            variance = sum(ImageStat.Stat(image).var) / 3
            # A low-variance image can be a valid flat-color slide. Treat only
            # near-white low-variance pages as likely blank; keep other flat
            # designs for a human review instead of auto-failing them.
            mean_luminance = sum(ImageStat.Stat(image).mean) / 3
            blank = variance < 3.0 and mean_luminance > 248
            too_small = width < 800 or height < 450
            status = "AUTO_FAIL" if blank else "AUTO_WARNING" if too_small else "REVIEW_REQUIRED"
            review = approvals.get(index)
            if review:
                status = "HUMAN_APPROVED"
            name = f"slide_{index:03d}.png"
            dest = out / name
            image.save(dest, format="PNG", optimize=True)
            thumb = image.copy(); thumb.thumbnail((360, 203)); thumbs.append((index, thumb.copy()))
            rows.append({"page": index, "source_render": str(image_path.resolve()), "preview": name,
                         "page_type": "unknown", "elements": "rendered page image only; object inventory not inferred",
                         "issues": "Blank/near-blank page" if blank else ("Low-resolution rendering" if too_small else "Human visual review still required"),
                         "status": status, "width_px": width, "height_px": height,
                         "reviewer": review.get("reviewer", "") if review else "", "reviewed_at": review.get("reviewed_at", "") if review else ""})
    if thumbs:
        cols = 4; rows_count = (len(thumbs) + cols - 1) // cols
        sheet = Image.new("RGB", (cols * 380, rows_count * 230), "#d8dee8")
        from PIL import ImageDraw
        draw = ImageDraw.Draw(sheet)
        for i, (page, thumb) in enumerate(thumbs):
            x, y = (i % cols) * 380 + 10, (i // cols) * 230 + 20
            sheet.paste(thumb, (x, y)); draw.text((x, y - 16), f"Page {page}", fill="#111827")
        sheet.save(out / "contact_sheet.png", optimize=True)
    with (out / "visual_audit_report.csv").open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]) if rows else ["page", "status"]); writer.writeheader(); writer.writerows(rows)
    lines = ["# Rendered-page visual audit", "", f"Pages found: {len(rows)}", "", "| Page | Status | Size | Issue |", "|---:|---|---:|---|"]
    lines.extend(f"| {r['page']} | {r['status']} | {r['width_px']}×{r['height_px']} | {r['issues']} |" for r in rows)
    if not rows: lines.append("No rendered page images supplied; visual review is BLOCKED.")
    lines += ["", "Automated image checks do not approve readability, data accuracy, chart integrity, clipping or source mapping. HUMAN_APPROVED is only recorded when a reviewer is named for that page in the supplied review file."]
    (out / "visual_audit_report.md").write_text("\n".join(lines), encoding="utf-8")
    return {"page_count": len(rows), "pages": rows, "human_approved": sum(x["status"] == "HUMAN_APPROVED" for x in rows),
            "review_file": str(Path(review_file).resolve()) if review_file else "", "status": "REVIEW_REQUIRED" if rows else "BLOCKED"}
