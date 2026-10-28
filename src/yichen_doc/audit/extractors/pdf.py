from __future__ import annotations

from pathlib import Path
import hashlib
from pypdf import PdfReader
from ._common import add


def extract_pdf(path: Path):
    reader = PdfReader(str(path))
    units = []
    for pi, page in enumerate(reader.pages, 1):
        text = page.extract_text(extraction_mode="layout") or page.extract_text() or ""
        for bi, block in enumerate((x.strip() for x in text.split("\n\n")), 1):
            item = add(path, f"page[{pi:04d}]/text[{bi:04d}]", "paragraph", block, f"page {pi}")
            if item: units.append(item)
        for ai, annotation in enumerate(page.get("/Annots", []), 1):
            try:
                obj = annotation.get_object()
                uri = obj.get("/A", {}).get("/URI", "")
            except Exception:
                uri = ""
            if uri:
                item = add(path, f"page[{pi:04d}]/annotation[{ai:03d}]", "citation", str(uri), f"page {pi}")
                if item: units.append(item)
        try:
            for ii, image in enumerate(page.images, 1):
                blob = image.data
                item = add(path, f"page[{pi:04d}]/image[{ii:03d}]", "image_resource",
                           f"{image.name}; bytes={len(blob)}; sha256={hashlib.sha256(blob).hexdigest()}", f"page {pi}")
                if item: units.append(item)
        except Exception:
            # Some PDFs expose image XObjects that pypdf cannot decode. The
            # extractor records only extractable images; package audit still
            # identifies structural failures separately.
            pass
    return units
