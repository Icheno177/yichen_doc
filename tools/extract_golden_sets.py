from __future__ import annotations

from collections import Counter
from pathlib import Path
import json
import zipfile
import argparse
from lxml import etree
from docx import Document
from docx.oxml.ns import qn
from pptx import Presentation

ROOT = Path(__file__).resolve().parents[1]
WORD: Path
PPT: Path
OUTW = ROOT / "golden_sets" / "word"; OUTP = ROOT / "golden_sets" / "powerpoint"
OUTW.mkdir(parents=True, exist_ok=True); OUTP.mkdir(parents=True, exist_ok=True)
NS = {"w":"http://schemas.openxmlformats.org/wordprocessingml/2006/main", "a":"http://schemas.openxmlformats.org/drawingml/2006/main", "p":"http://schemas.openxmlformats.org/presentationml/2006/main"}

def word_manifest():
    doc=Document(WORD); style_counts=Counter(p.style.name for p in doc.paragraphs if p.text.strip())
    run_fonts=Counter(); sizes=Counter(); colors=Counter(); bold=Counter(); alignments=Counter(); indents=Counter(); line_spaces=Counter(); direct_east=Counter()
    for p in doc.paragraphs:
        if not p.text.strip(): continue
        alignments[str(p.alignment)] += 1
        if p.paragraph_format.first_line_indent is not None: indents[round(p.paragraph_format.first_line_indent.pt,1)] += 1
        if p.paragraph_format.line_spacing is not None: line_spaces[str(p.paragraph_format.line_spacing)] += 1
        for r in p.runs:
            if not r.text: continue
            run_fonts[r.font.name or "inherited"] += len(r.text)
            sizes[str(r.font.size.pt if r.font.size else "inherited")] += len(r.text)
            colors[str(r.font.color.rgb if r.font.color and r.font.color.rgb else "inherited")] += len(r.text)
            bold[str(r.bold if r.bold is not None else "inherited")] += len(r.text)
    with zipfile.ZipFile(WORD) as z:
        document=etree.fromstring(z.read("word/document.xml")); styles=etree.fromstring(z.read("word/styles.xml")); theme_files=[n for n in z.namelist() if n.startswith("word/theme/") and n.endswith(".xml")]
        theme=etree.fromstring(z.read(theme_files[0])) if theme_files else None
        defaults=styles.find("w:docDefaults",NS)
        default_rpr=defaults.find("w:rPrDefault/w:rPr",NS) if defaults is not None else None
        default_fonts=default_rpr.find("w:rFonts",NS) if default_rpr is not None else None
        default_size=default_rpr.find("w:sz",NS) if default_rpr is not None else None
        direct_runs=document.xpath(".//w:rPr",namespaces=NS)
        direct = {"run_properties":len(direct_runs),"east_asia_font_overrides":Counter(x.get("eastAsia") for r in direct_runs if (x:=r.find("w:rFonts",NS)) is not None and x.get("eastAsia")),"font_size_half_points":Counter(x.get("val") for r in direct_runs if (x:=r.find("w:sz",NS)) is not None),"bold_marks":sum(r.find("w:b",NS) is not None for r in direct_runs),"color_overrides":Counter(x.get("val") for r in direct_runs if (x:=r.find("w:color",NS)) is not None)}
        tables=document.xpath(".//w:tbl",namespaces=NS)
        table_borders=Counter()
        table_margins=Counter()
        for t in tables:
            for b in t.xpath(".//w:tblBorders/*",namespaces=NS): table_borders[(etree.QName(b).localname,b.get(qn("val")),b.get(qn("sz")),b.get(qn("color")))] += 1
            for m in t.xpath(".//w:tcMar/*",namespaces=NS): table_margins[(etree.QName(m).localname,m.get(qn("w")),m.get(qn("type")))] += 1
        theme_fonts={}
        if theme is not None:
            for kind in ("majorFont","minorFont"):
                n=theme.find(f".//a:{kind}",NS)
                if n is not None:
                    lat=n.find("a:latin",NS); ea=n.find("a:ea",NS)
                    theme_fonts[kind]={"latin":lat.get("typeface") if lat is not None else None,"eastAsia":ea.get("typeface") if ea is not None else None}
    sections=[]
    for sec in doc.sections:
        sections.append({"page_width_in":round(sec.page_width/914400,3),"page_height_in":round(sec.page_height/914400,3),"orientation":str(sec.orientation),"margins_in":{"top":round(sec.top_margin/914400,3),"bottom":round(sec.bottom_margin/914400,3),"left":round(sec.left_margin/914400,3),"right":round(sec.right_margin/914400,3)},"different_first_page_header_footer":sec.different_first_page_header_footer})
    def counter_map(c): return [{"value":str(k),"count":v} for k,v in c.most_common()]
    manifest={"system":"yichen_doc","source":{"reference_type":"user-selected private DOCX","source_path_recorded":False,"content_copied":False},"document":{"sections":sections},"style_usage":counter_map(style_counts),"effective_format_frequency_by_text_characters":{"font":counter_map(run_fonts),"size_pt":counter_map(sizes),"color":counter_map(colors),"bold":counter_map(bold)},"paragraph_format_frequency":{"alignment":counter_map(alignments),"first_line_indent_pt":counter_map(indents),"line_spacing":counter_map(line_spaces)},"style_definitions":{},"ooxml":{"document_defaults":{"latin_font":default_fonts.get("ascii") if default_fonts is not None else None,"east_asia_font":default_fonts.get("eastAsia") if default_fonts is not None else None,"font_size_half_points":default_size.get("val") if default_size is not None else None},"theme_fonts":theme_fonts,"direct_format_summary":{"east_asia_font_overrides":counter_map(direct["east_asia_font_overrides"]),"font_size_half_points":counter_map(direct["font_size_half_points"]),"color_overrides":counter_map(direct["color_overrides"])},"table_borders":counter_map(table_borders),"table_cell_margins":counter_map(table_margins)}}
    for name in ("Normal","Title","Heading 1","Heading 2","Heading 3","Heading 4"):
        try:
            s=doc.styles[name]; f=s.font; pf=s.paragraph_format
            manifest["style_definitions"][name]={"font_latin":f.name,"font_size_pt":f.size.pt if f.size else None,"bold":f.bold,"italic":f.italic,"color":str(f.color.rgb) if f.color and f.color.rgb else None,"east_asia_font":s._element.rPr.rFonts.get(qn("w:eastAsia")) if s._element.rPr is not None and s._element.rPr.rFonts is not None else None,"space_before_pt":pf.space_before.pt if pf.space_before else None,"space_after_pt":pf.space_after.pt if pf.space_after else None,"line_spacing":pf.line_spacing,"first_line_indent_pt":pf.first_line_indent.pt if pf.first_line_indent else None}
        except KeyError: pass
    (OUTW/"style_manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
    (OUTW/"style_audit.md").write_text(f'''# Word Golden Set 样式审计\n\n日期：2026-10-25。来源为本地用户指定的私有DOCX。清单不记录源路径、文件名或哈希；只发布通用样式属性，不复制原文、表格内容、数据或图片。\n\n## 真实版式\n\n- {len(doc.sections)}个分节；页面约{sections[0]['page_width_in']}×{sections[0]['page_height_in']}英寸（A4纵向）；页边距上/下{sections[0]['margins_in']['top']}/{sections[0]['margins_in']['bottom']}、左/右{sections[0]['margins_in']['left']}/{sections[0]['margins_in']['right']}英寸。\n- 正文样式以Normal为主；样式使用、直接格式、东亚字体、字色、字号、段落间距、标题层级及表格边框/单元格边距统计见JSON。\n- DOCX主题和段落样式存在直接格式覆盖；提取时保留“继承”状态，不能把局部格式误判为文档默认值。具体文字字符频次用于识别实际表现，样式XML单独记录规则定义。\n- 模板不包含来源文档中的表格内容。\n\n## 使用边界\n\n该Golden Set用于版式继承，字体缺失时须报告回退情况。模板是空白生产骨架，不是原报告副本。改用其他Word来源前应重新运行提取脚本并复核冲突样式。\n''',encoding="utf-8")

def ppt_manifest():
    deck=Presentation(PPT); fonts=Counter(); sizes=Counter(); colors=Counter(); fills=Counter(); types=Counter(); image_positions=[]; table_count=chart_count=0
    W=deck.slide_width; H=deck.slide_height
    for si,sl in enumerate(deck.slides,1):
        for sh in sl.shapes:
            types[str(sh.shape_type)]+=1
            if sh.has_table: table_count += 1
            if sh.has_chart: chart_count += 1
            if sh.shape_type==13:
                image_positions.append({"slide":si,"x_norm":round(sh.left/W,4),"y_norm":round(sh.top/H,4),"w_norm":round(sh.width/W,4),"h_norm":round(sh.height/H,4)})
            if sh.has_text_frame:
                for p in sh.text_frame.paragraphs:
                    for r in p.runs:
                        if not r.text.strip(): continue
                        fonts[r.font.name or "inherited"] += len(r.text)
                        sizes[str(r.font.size.pt if r.font.size else "inherited")] += len(r.text)
                        try: colors[str(r.font.color.rgb or r.font.color.theme_color or "inherited")] += len(r.text)
                        except Exception: colors["inherited"] += len(r.text)
            if sh.shape_type==19:
                for row in sh.table.rows:
                    for cell in row.cells:
                        for p in cell.text_frame.paragraphs:
                            for r in p.runs:
                                if not r.text.strip(): continue
                                fonts[r.font.name or "inherited"] += len(r.text); sizes[str(r.font.size.pt if r.font.size else "inherited")] += len(r.text)
    palette={}
    with zipfile.ZipFile(PPT) as z:
        theme_files=[n for n in z.namelist() if n.startswith("ppt/theme/") and n.endswith(".xml")]
        if theme_files:
            theme=etree.fromstring(z.read(theme_files[0]))
            scheme=theme.find(".//a:clrScheme",NS)
            if scheme is not None:
                for entry in scheme:
                    child=entry[0] if len(entry) else None
                    palette[etree.QName(entry).localname]=child.get("val") if child is not None else None
    manifest={"system":"yichen_doc","source":{"reference_type":"user-selected private PPTX","source_path_recorded":False,"content_copied":False},"canvas":{"width_in":round(W/914400,3),"height_in":round(H/914400,3),"ratio":round(W/H,4)},"theme_palette":palette,"effective_format_frequency_by_text_characters":{"font":counter_map(fonts),"size_pt":counter_map(sizes),"color":counter_map(colors)},"layout_observations":{"page_margin_pattern":"Use a consistent header, title area, content region, and footer with page number.","logo_pattern":"Use a replaceable logo placeholder; do not copy identity assets from the private reference.","charts_and_tables":"Use editable native text, shapes, charts, and tables where supported."}}
    (OUTP/"theme_manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
    (OUTP/"layout_audit.md").write_text(f'''# PowerPoint Golden Set 布局审计\n\n来源为本地用户指定的私有PPTX；清单不记录源路径、文件名、哈希或页面内容。画布{manifest['canvas']['width_in']}×{manifest['canvas']['height_in']}英寸，仅输出通用排版和字体/颜色设置。\n\n- 页眉与结论标题位于上方；主体从页面约六分之一高度开始；页码与授权信息位于底部。\n- 图片主要用于品牌和产品识别，Logo在不同页面的位置与尺寸不完全统一，因此新模板使用可替换Logo占位框。\n- 文字、数据图表和表格尽量保持原生可编辑。不同页面类型的密度差异较大，模板提供封面、结论、数据图表和对比表的基础骨架，不要求所有页面使用同一网格。\n- 实际字体和颜色设置保存在`theme_manifest.json`，不包含来源页码、对象数量、Logo或图片位置。\n\n该文件作为风格参考。研究结论、数字和原企业资产没有被带入通用模板。\n''',encoding="utf-8")

def counter_map(c): return [{"value":str(k),"count":v} for k,v in c.most_common()]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract style-only Golden Set manifests from user-selected Office files.")
    parser.add_argument("--word", required=True, type=Path, help="Path to the Word style reference DOCX")
    parser.add_argument("--ppt", required=True, type=Path, help="Path to the PowerPoint style reference PPTX")
    args = parser.parse_args()
    WORD = args.word.resolve(); PPT = args.ppt.resolve()
    if not WORD.is_file() or not PPT.is_file(): parser.error("Both --word and --ppt must point to existing files")
    word_manifest(); ppt_manifest(); print("Golden Set manifests and audits written")
