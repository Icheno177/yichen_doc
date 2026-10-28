from __future__ import annotations

from html import escape
from pathlib import Path
import json
import base64
import mimetypes


def _chart(block: dict) -> str:
    cats = block.get("categories", []); series = block.get("series", [])
    maximum = max((abs(v) for s in series for v in s.get("values", []) if isinstance(v, (int, float))), default=1) or 1
    bars = []
    for i, cat in enumerate(cats):
        values = "".join(f'<span class="bar" style="width:{max(0, float(s["values"][i])/maximum*78):.1f}%" title="{escape(str(s["name"]))}: {escape(str(s["values"][i]))}"></span>' for s in series)
        labels = " · ".join(f'{escape(str(s["name"]))}: {escape(str(s["values"][i]))}' for s in series)
        bars.append(f'<div class="chart-row"><b>{escape(str(cat))}</b><div>{values}<small>{labels}</small></div></div>')
    return '<figure class="chart"><figcaption>' + escape(block.get("label", "Chart")) + f' <small>{escape(block.get("unit", ""))}</small></figcaption>' + ''.join(bars) + '</figure>'


def render(content: dict, output: str | Path, base_dir: str | Path = ".") -> Path:
    out = Path(output); meta = content["metadata"]; title = escape(meta["title"])
    css = """*{box-sizing:border-box}body{--page:#f3f4f6;--surface:#fff;--ink:#202124;--muted:#5e6268;--line:#d7dadd;--soft:#f2f3f4;--accent:#a92332;margin:0;background:var(--page);color:var(--ink);font:16px/1.65 'Microsoft YaHei',Arial,sans-serif}body.dark{--page:#17191c;--surface:#222529;--ink:#eef0f2;--muted:#b7bbc0;--line:#454a50;--soft:#30343a;--accent:#e16a77}header{padding:3rem max(calc((100vw - 1120px)/2),6vw);background:#202124;color:#fff}header h1{font-size:2.2rem;line-height:1.25;margin:.5rem 0}header .accent{width:48px;height:5px;background:#a92332}main{max-width:1120px;margin:2rem auto;padding:0 1rem}section,article{background:var(--surface);padding:1.6rem 2rem;margin:1rem 0;border-radius:10px;box-shadow:0 2px 12px #0000000c}h2{border-bottom:1px solid var(--line);padding-bottom:.55rem}h3{color:var(--accent)}.summary{font-size:1.12rem;border-left:4px solid var(--accent);padding:.8rem 1rem;background:var(--soft)}.tag{color:var(--accent);font-weight:700;font-size:.82rem}table{width:100%;border-collapse:collapse;margin:1rem 0}th{background:#202124;color:white;text-align:left;cursor:pointer}td,th{padding:.65rem;border:1px solid var(--line)}tr:nth-child(even){background:var(--soft)}.chart-row{display:grid;grid-template-columns:8rem 1fr;gap:1rem;margin:.55rem 0}.chart-row>div{position:relative;background:var(--soft);min-height:2rem;padding:.2rem}.bar{display:inline-block;background:var(--accent);height:1rem;margin-right:.25rem}.chart-row small{margin-left:.5rem}figure{margin:1.2rem 0;padding:1rem;background:var(--soft);border:1px solid var(--line);border-radius:8px}figcaption{font-weight:700;margin-bottom:.8rem}nav{display:flex;gap:.5rem;flex-wrap:wrap}nav a{color:var(--ink);text-decoration:none;border:1px solid var(--line);padding:.25rem .55rem;border-radius:5px}input,button{padding:.65rem;border:1px solid #bbb;border-radius:6px}input{width:100%}button{cursor:pointer}footer{max-width:1120px;margin:2rem auto;color:var(--muted);padding:0 1rem;font-size:.85rem}@media(max-width:680px){header{padding:2rem 1rem}.chart-row{grid-template-columns:1fr;gap:.2rem}section,article{padding:1rem}}@media print{body{background:#fff;color:#000}section,article{box-shadow:none;break-inside:avoid}nav,input,button{display:none}}"""
    logo_html = ""
    if meta.get("logo_path"):
        logo_path = (Path(base_dir) / meta["logo_path"]).resolve(); mime = mimetypes.guess_type(logo_path.name)[0] or "application/octet-stream"
        logo_html = f'<img src="data:{mime};base64,{base64.b64encode(logo_path.read_bytes()).decode("ascii")}" alt="Logo" style="max-width:140px;max-height:64px">'
    parts = [f'<!doctype html><html lang="{escape(meta.get("language", "zh-CN"))}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{title}</title><style>{css}</style></head><body>', '<header><div class="accent"></div>', logo_html, f'<h1>{title}</h1>', f'<p>{escape(meta.get("subtitle", ""))}</p><p>{escape(meta.get("date", ""))} · {escape(meta.get("confidentiality", ""))}</p><button id="themeToggle" type="button" aria-pressed="false">切换深浅主题</button></header><main>']
    parts.append(f'<section><h2>决策摘要</h2><p><b>{escape(content["decision"]["question"])}</b></p><p class="summary">{escape(content["decision"]["answer"])}</p></section>')
    parts.append('<section><h2>导航</h2><nav>' + ''.join(f'<a href="#{escape(s["id"])}">{escape(s["title"])}</a>' for s in content.get("sections", [])) + '</nav></section>')
    parts.append('<input id="tableSearch" placeholder="筛选报告表格内容" aria-label="筛选表格内容">')
    for section in content.get("sections", []):
        parts.append(f'<section id="{escape(section["id"])}"><h2>{escape(section["title"])}</h2>')
        if section.get("conclusion"): parts.append(f'<p class="summary">{escape(section["conclusion"])}</p>')
        for b in section.get("blocks", []):
            kind = b["type"]
            if kind == "heading": parts.append(f'<h3>{escape(b.get("text", ""))}</h3>')
            elif kind in ("paragraph", "callout", "formula", "citation"):
                parts.append(f'<p><span class="tag">{escape(b.get("evidence_type", b.get("label", "")))}</span> {escape(b.get("text", b.get("formula", "")))}</p>')
            elif kind == "metric": parts.append(f'<article><span class="tag">{escape(b.get("label", "Metric"))}</span><h3>{escape(str(b.get("value", "")))} {escape(b.get("unit", ""))}</h3></article>')
            elif kind == "table":
                parts.append('<table><thead><tr>' + ''.join(f'<th>{escape(str(h))}</th>' for h in b["headers"]) + '</tr></thead><tbody>')
                parts.extend('<tr>' + ''.join(f'<td>{escape(str(v))}</td>' for v in row) + '</tr>' for row in b.get("rows", [])); parts.append('</tbody></table>')
            elif kind == "chart": parts.append(_chart(b))
            elif kind == "image":
                image_path = (Path(base_dir) / b["image_path"]).resolve(); mime = mimetypes.guess_type(image_path.name)[0] or "application/octet-stream"
                encoded = base64.b64encode(image_path.read_bytes()).decode("ascii")
                parts.append(f'<figure><img src="data:{mime};base64,{encoded}" alt="{escape(b.get("alt", ""))}" style="max-width:100%"><figcaption>{escape(b.get("alt", ""))}</figcaption></figure>')
        parts.append('</section>')
    parts.append('<section id="sources"><h2>来源</h2><ol>')
    for s in content.get("sources", []):
        url = f'<a href="{escape(s["url"])}">{escape(s["url"])}</a>' if s.get("url") else ''
        parts.append(f'<li><b>{escape(s["id"])}</b> {escape(s["title"])} · {escape(s.get("organization", ""))} · 等级 {escape(s.get("grade", ""))} {url}<br>{escape(s.get("limitations", ""))}</li>')
    parts.append('</ol></section></main><footer>出版人：谢翊忱 · yichen_doc · 可通过浏览器打印为PDF</footer><script>document.getElementById("tableSearch").addEventListener("input",e=>{const q=e.target.value.toLowerCase();document.querySelectorAll("tbody tr").forEach(r=>r.hidden=!r.innerText.toLowerCase().includes(q))});document.getElementById("themeToggle").addEventListener("click",e=>{document.body.classList.toggle("dark");e.currentTarget.setAttribute("aria-pressed",String(document.body.classList.contains("dark")))});document.querySelectorAll("table thead th").forEach((h,i)=>h.addEventListener("click",()=>{const body=h.closest("table").tBodies[0];const rows=[...body.rows];const asc=h.dataset.sort!=="asc";rows.sort((a,b)=>{const x=a.cells[i].innerText.trim(),y=b.cells[i].innerText.trim(),nx=Number(x.replace(/[,¥%]/g,"")),ny=Number(y.replace(/[,¥%]/g,""));return Number.isFinite(nx)&&Number.isFinite(ny)?(nx-ny)*(asc?1:-1):x.localeCompare(y,"zh-CN")*(asc?1:-1)});rows.forEach(r=>body.appendChild(r));h.dataset.sort=asc?"asc":"desc"}));</script></body></html>')
    out.parent.mkdir(parents=True, exist_ok=True); out.write_text(''.join(parts), encoding="utf-8"); return out
