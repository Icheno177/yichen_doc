from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
from ._common import add


class _Parser(HTMLParser):
    def __init__(self):
        super().__init__(); self.units = []; self.captures = []; self.table = 0; self.row = 0; self.cell = 0
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag in {"h1", "h2", "h3", "h4", "p", "li", "td", "th", "figcaption", "blockquote"}:
            self.captures.append([tag, [], attrs])
            if tag == "td" or tag == "th": self.cell += 1
        elif tag == "table": self.table += 1; self.row = 0; self.cell = 0
        elif tag == "tr": self.row += 1; self.cell = 0
        elif tag == "img": self.units.append(("image", attrs.get("alt", ""), attrs.get("src", "")))
        elif tag == "a" and attrs.get("href", "").startswith("http"):
            self.units.append(("citation", attrs.get("href", ""), attrs.get("href", "")))
    def handle_data(self, data):
        for capture in self.captures: capture[1].append(data)
    def handle_endtag(self, tag):
        for index in range(len(self.captures) - 1, -1, -1):
            if self.captures[index][0] == tag:
                kind, parts, attrs = self.captures.pop(index)
                loc = f"table[{self.table}]/row[{self.row}]/cell[{self.cell}]" if kind in {"td", "th"} else f"element[{len(self.units)+1}]"
                self.units.append(("heading" if kind.startswith("h") else ("table_cell" if kind in {"td", "th"} else "paragraph"), "".join(parts).strip(), loc))
                break


def extract_html(path: Path):
    parser = _Parser(); parser.feed(path.read_text(encoding="utf-8", errors="replace"))
    units = []
    for i, (kind, text, loc) in enumerate(parser.units, 1):
        item = add(path, f"html/{loc or i}", kind, text)
        if item: units.append(item)
    return units
