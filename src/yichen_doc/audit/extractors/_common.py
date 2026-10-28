from __future__ import annotations

import re
from pathlib import Path
from ..schemas import ContentUnit, sha256_file, unit_id

NUMBER_RE = re.compile(r"(?<!\w)[+-]?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?\s*(?:%|％|pp|bp|万元|亿元|元|美元|欧元|亿欧元|万|亿|年|月|天|小时|分钟|席位|次)?", re.I)
CITATION_RE = re.compile(r"\([A-Z][A-Za-z .&'-]+,\s*\d{4}[a-z]?\)|\[[0-9,; –-]+\]|https?://\S+", re.I)


def add(path: Path, locator: str, kind: str, text: str, section: str = "") -> ContentUnit | None:
    text = str(text or "").strip()
    if not text:
        return None
    digest = sha256_file(path)
    uid = unit_id(digest, locator, text)
    import hashlib
    text_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
    return ContentUnit(uid, str(path.resolve()), digest, locator, section, kind, text,
                       [n.strip() for n in NUMBER_RE.findall(text)], CITATION_RE.findall(text), text_hash)
