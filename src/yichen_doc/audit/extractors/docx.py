from __future__ import annotations

from pathlib import Path
import hashlib
from docx import Document
from ._common import add


def extract_docx(path: Path):
    doc = Document(path)
    units = []
    section = ""
    pno = 0
    tno = 0
    for child in doc.element.body.iterchildren():
        tag = child.tag.rsplit("}", 1)[-1]
        if tag == "p":
            pno += 1
            from docx.text.paragraph import Paragraph
            para = Paragraph(child, doc)
            text = para.text
            style = para.style.name if para.style else ""
            kind = "heading" if style.lower().startswith("heading") or style.lower() in {"title", "subtitle"} else "paragraph"
            if kind == "heading" and text:
                section = text
            item = add(path, f"body/paragraph[{pno:05d}]", kind, text, section)
            if item: units.append(item)
        elif tag == "tbl":
            tno += 1
            from docx.table import Table
            table = Table(child, doc)
            for ri, row in enumerate(table.rows, 1):
                for ci, cell in enumerate(row.cells, 1):
                    item = add(path, f"body/table[{tno:04d}]/row[{ri:04d}]/cell[{ci:03d}]", "table_cell", cell.text, section)
                    if item: units.append(item)
    for i, rel in enumerate(doc.part.rels.values(), 1):
        if "image" in rel.reltype:
            blob = rel.target_part.blob
            item = add(path, f"resources/image[{i:04d}]", "image_resource",
                       f"{rel.target_ref}; bytes={len(blob)}; sha256={hashlib.sha256(blob).hexdigest()}", section)
            if item: units.append(item)
    return units
