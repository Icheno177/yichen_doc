from __future__ import annotations

from pathlib import Path
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn


def _set_run(run, font: str, size: float, bold: bool = False, color: str = "202124") -> None:
    run.font.name = font; run.font.size = Pt(size); run.font.bold = bold
    run.font.color.rgb = RGBColor.from_string(color)
    rpr = run._element.get_or_add_rPr(); rfonts = rpr.rFonts
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts"); rpr.append(rfonts)
    rfonts.set(qn("w:eastAsia"), font); rfonts.set(qn("w:ascii"), font); rfonts.set(qn("w:hAnsi"), font)


def _field(paragraph, instruction: str) -> None:
    run = paragraph.add_run(); begin = OxmlElement("w:fldChar"); begin.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText"); instr.set(qn("xml:space"), "preserve"); instr.text = instruction
    separate = OxmlElement("w:fldChar"); separate.set(qn("w:fldCharType"), "separate")
    text = OxmlElement("w:t"); text.text = "1"
    end = OxmlElement("w:fldChar"); end.set(qn("w:fldCharType"), "end")
    for el in (begin, instr, separate, text, end): run._r.append(el)


def _cell_shading(cell, fill: str) -> None:
    tc_pr = cell._tc.get_or_add_tcPr(); shd = OxmlElement("w:shd"); shd.set(qn("w:fill"), fill); tc_pr.append(shd)


def render(content: dict, output: str | Path, base_dir: str | Path = ".") -> Path:
    out = Path(output); base = Path(base_dir)
    theme = content.get("metadata", {}).get("theme", {})
    font = theme.get("font", "Microsoft YaHei"); accent = theme.get("accent", "A92332")
    doc = Document(); sec = doc.sections[0]
    doc.core_properties.author = "谢翊忱"
    doc.core_properties.last_modified_by = "谢翊忱"
    sec.top_margin = Inches(0.78); sec.bottom_margin = Inches(0.75); sec.left_margin = Inches(0.9); sec.right_margin = Inches(0.9)
    normal = doc.styles["Normal"]; normal.font.name = font; normal.font.size = Pt(10.5)
    normal._element.rPr.rFonts.set(qn("w:eastAsia"), font)
    for name, size in (("Heading 1", 17), ("Heading 2", 13), ("Heading 3", 11)):
        st = doc.styles[name]; st.font.name = font; st.font.size = Pt(size); st.font.bold = True; st.font.color.rgb = RGBColor.from_string(accent)
        st._element.rPr.rFonts.set(qn("w:eastAsia"), font)
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.space_before = Pt(92)
    if content["metadata"].get("logo_path"):
        logo = (base / content["metadata"]["logo_path"]).resolve()
        p.add_run().add_picture(str(logo), width=Inches(1.1))
        doc.add_paragraph()
    if content["metadata"].get("cover_image_path"):
        p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.add_run().add_picture(str((base / content["metadata"]["cover_image_path"]).resolve()), width=Inches(6.2))
        doc.add_paragraph()
    _set_run(p.add_run(content["metadata"]["title"]), font, 27, True, "202124")
    if content["metadata"].get("subtitle"):
        p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; _set_run(p.add_run(content["metadata"]["subtitle"]), font, 14, False, "5E6268")
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.space_before = Pt(22)
    _set_run(p.add_run(content["metadata"].get("date", "")), font, 11, False, "5E6268")
    if content["metadata"].get("confidentiality"):
        p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; _set_run(p.add_run(content["metadata"]["confidentiality"]), font, 9, False, "5E6268")
    doc.add_page_break()
    doc.add_heading("目录", 1)
    p = doc.add_paragraph(); _field(p, 'TOC \\o "1-3" \\h \\z \\u')
    doc.add_page_break()
    doc.add_heading("决策摘要", 1)
    doc.add_heading(content["decision"]["question"], 2)
    doc.add_paragraph(content["decision"]["answer"])
    for section in content.get("sections", []):
        doc.add_heading(section["title"], 1)
        if section.get("conclusion"):
            p = doc.add_paragraph(); _set_run(p.add_run(section["conclusion"]), font, 11, True, "202124")
        for block in section.get("blocks", []):
            kind = block["type"]
            if kind == "heading": doc.add_heading(block.get("text", ""), 2)
            elif kind in {"paragraph", "callout", "formula"}:
                p = doc.add_paragraph();
                if block.get("label"):
                    _set_run(p.add_run(block["label"] + "  "), font, 10.5, True, accent)
                p.add_run(block.get("text", block.get("formula", "")))
                if block.get("evidence_type"):
                    _set_run(p.add_run(f"  [{block['evidence_type']}]"), font, 8.5, False, "5E6268")
            elif kind == "metric":
                p = doc.add_paragraph(); _set_run(p.add_run(f"{block.get('label', '')}: {block.get('value', '')} {block.get('unit', '')}"), font, 13, True, accent)
            elif kind == "table":
                table = doc.add_table(rows=1, cols=len(block["headers"])); table.alignment = WD_TABLE_ALIGNMENT.CENTER; table.style = "Light Shading Accent 1"
                for i, val in enumerate(block["headers"]):
                    cell = table.rows[0].cells[i]; cell.text = str(val); _cell_shading(cell, accent)
                    for r in cell.paragraphs[0].runs: _set_run(r, font, 9, True, "FFFFFF")
                for row in block.get("rows", []):
                    cells = table.add_row().cells
                    for i, val in enumerate(row):
                        cells[i].text = str(val); cells[i].vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
                        for para in cells[i].paragraphs:
                            for r in para.runs: _set_run(r, font, 9, False)
            elif kind == "image":
                img = (base / block["image_path"]).resolve()
                p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p.add_run().add_picture(str(img), width=Inches(5.8))
                cap = doc.add_paragraph(block.get("alt", "")); cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
            elif kind == "chart":
                # A compact native Word table preserves exact chart data and remains editable.
                headers = ["类别"] + [s["name"] for s in block["series"]]
                rows = [[cat] + [series["values"][i] for series in block["series"]] for i, cat in enumerate(block["categories"])]
                chart_block = {"type": "table", "headers": headers, "rows": rows}
                table = doc.add_table(rows=1, cols=len(headers)); table.style = "Light Shading Accent 1"
                for i, val in enumerate(headers): table.rows[0].cells[i].text = str(val)
                for row in rows:
                    for i, val in enumerate(row): table.add_row().cells[i].text = str(val)
                p = doc.add_paragraph(f"圖表資料表（{block.get('unit', '')}）"); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        if section.get("conclusion"):
            doc.add_paragraph("")
    if content.get("sources"):
        doc.add_page_break(); doc.add_heading("来源与方法", 1)
        for source in content["sources"]:
            p = doc.add_paragraph(style="List Bullet")
            p.add_run(f"[{source['id']}] {source['title']}")
            if source.get("organization"): p.add_run(f" — {source['organization']}")
            if source.get("date"): p.add_run(f" ({source['date']})")
            if source.get("grade"): p.add_run(f" · 证据等级 {source['grade']}")
            if source.get("url"): p.add_run(f" · {source['url']}")
            if source.get("limitations"): p.add_run(f" · 限制：{source['limitations']}")
    for section in doc.sections:
        footer = section.footer.paragraphs[0]; footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
        footer.add_run("出版人：谢翊忱  ·  yichen_doc  ·  "); _field(footer, "PAGE")
    settings=doc.settings.element; update=OxmlElement('w:updateFields'); update.set(qn('w:val'),'true'); settings.append(update)
    out.parent.mkdir(parents=True, exist_ok=True); doc.save(out); return out
