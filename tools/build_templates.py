from pathlib import Path
import json
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from pptx import Presentation
from pptx.util import Inches as PIn, Pt as PPt
from pptx.dml.color import RGBColor as PRGB
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.chart import XL_CHART_TYPE
from pptx.chart.data import CategoryChartData

ROOT=Path(__file__).resolve().parents[1]
WORD_MAN=json.loads((ROOT/'golden_sets/word/style_manifest.json').read_text(encoding='utf-8'))
PPT_MAN=json.loads((ROOT/'golden_sets/powerpoint/theme_manifest.json').read_text(encoding='utf-8'))

def field(p, name):
    r=p.add_run(); begin=OxmlElement('w:fldChar');begin.set(qn('w:fldCharType'),'begin');instr=OxmlElement('w:instrText');instr.set(qn('xml:space'),'preserve');instr.text=name
    sep=OxmlElement('w:fldChar');sep.set(qn('w:fldCharType'),'separate');t=OxmlElement('w:t');t.text='1';end=OxmlElement('w:fldChar');end.set(qn('w:fldCharType'),'end')
    for e in (begin,instr,sep,t,end):r._r.append(e)

def build_docx():
    d=Document(); sec=d.sections[0]; s=WORD_MAN['document']['sections'][0]
    sec.page_width=Inches(s['page_width_in']);sec.page_height=Inches(s['page_height_in'])
    for k,v in s['margins_in'].items():setattr(sec,{'top':'top_margin','bottom':'bottom_margin','left':'left_margin','right':'right_margin'}[k], Inches(v))
    normal=WORD_MAN['style_definitions']['Normal']; n=d.styles['Normal']; n.font.name=normal['font_latin'] or 'Times New Roman'; n.font.size=Pt(normal['font_size_pt'] or 12)
    n._element.rPr.rFonts.set(qn('w:eastAsia'),normal['east_asia_font'] or 'Microsoft YaHei')
    n.paragraph_format.space_after=Pt(normal['space_after_pt'] or 6); n.paragraph_format.line_spacing=normal['line_spacing'] or 1.15
    for name in ('Title','Heading 1','Heading 2','Heading 3','Heading 4'):
        if name not in WORD_MAN['style_definitions']:continue
        data=WORD_MAN['style_definitions'][name]; st=d.styles[name]
        if data.get('font_size_pt'):st.font.size=Pt(data['font_size_pt'])
        if data.get('bold') is not None:st.font.bold=data['bold']
        if data.get('color'):st.font.color.rgb=RGBColor.from_string(data['color'])
        st.font.name=normal['font_latin'] or 'Times New Roman';st._element.rPr.rFonts.set(qn('w:eastAsia'),normal['east_asia_font'] or 'Microsoft YaHei')
        if data.get('space_before_pt') is not None:st.paragraph_format.space_before=Pt(data['space_before_pt'])
        if data.get('space_after_pt') is not None:st.paragraph_format.space_after=Pt(data['space_after_pt'])
    p=d.add_paragraph();p.alignment=WD_ALIGN_PARAGRAPH.CENTER;p.paragraph_format.space_before=Pt(48);p.add_run('[企业Logo占位]').font.size=Pt(10)
    p=d.add_paragraph(style='Title');p.alignment=WD_ALIGN_PARAGRAPH.CENTER;p.paragraph_format.space_before=Pt(48);p.add_run('研究报告标题')
    p=d.add_paragraph();p.alignment=WD_ALIGN_PARAGRAPH.CENTER;p.add_run('副标题 / 研究范围')
    p=d.add_paragraph();p.alignment=WD_ALIGN_PARAGRAPH.CENTER;p.add_run('报告日期：YYYY-MM-DD')
    p=d.add_paragraph();p.alignment=WD_ALIGN_PARAGRAPH.CENTER;p.add_run('资料级别 / 授权范围')
    d.add_page_break();d.add_heading('目录',level=1);p=d.add_paragraph();field(p,'TOC \\o "1-3" \\h \\z \\u');d.add_page_break()
    d.add_heading('执行摘要',level=1);d.add_paragraph('核心问题、结论、决策动作及关键证据。')
    d.add_heading('研究章节',level=1);d.add_heading('二级标题',level=2);d.add_heading('三级标题',level=3);d.add_paragraph('正文段落。事实、假设、计算与判断按需标记。')
    t=d.add_table(rows=2,cols=3);t.style='Table Grid';t.rows[0].cells[0].text='指标';t.rows[0].cells[1].text='数值 / 单位';t.rows[0].cells[2].text='来源 / 口径';t.rows[1].cells[0].text='示例字段';t.rows[1].cells[1].text='待填';t.rows[1].cells[2].text='来源编号'
    d.add_paragraph('表1：表格标题与来源口径')
    d.add_heading('来源与方法',level=1);d.add_paragraph('[S-01] 机构 / 文件 / 日期 / 网址 / 限制')
    h=sec.header.paragraphs[0];h.text='研究报告  |  [组织 / Logo]';h.alignment=WD_ALIGN_PARAGRAPH.RIGHT
    f=sec.footer.paragraphs[0];f.alignment=WD_ALIGN_PARAGRAPH.CENTER;f.add_run('内部材料  ·  ');field(f,'PAGE')
    d.save(ROOT/'templates/docx/research_report.docx')

def build_pptx():
    # Direct text color frequency in the reference is more representative than its generic Office theme defaults.
    colors=[x['value'] for x in PPT_MAN['effective_format_frequency_by_text_characters']['color']]
    ink=next((x for x in colors if x=='202124'),'202124'); red=next((x for x in colors if x=='A92332'),'A92332'); gray=next((x for x in colors if x=='5E6268'),'5E6268')
    ppt=Presentation();ppt.slide_width=PIn(PPT_MAN['canvas']['width_in']);ppt.slide_height=PIn(PPT_MAN['canvas']['height_in'])
    white=PRGB(255,255,255);dark=PRGB.from_string(ink); accent=PRGB.from_string(red); muted=PRGB.from_string(gray); light=PRGB.from_string('F2F3F4')
    # Cover
    sl=ppt.slides.add_slide(ppt.slide_layouts[6]);sl.background.fill.solid();sl.background.fill.fore_color.rgb=dark
    sh=sl.shapes.add_shape(MSO_SHAPE.RECTANGLE,PIn(.44),PIn(.45),PIn(.42),PIn(.06));sh.fill.solid();sh.fill.fore_color.rgb=accent;sh.line.fill.background()
    tx=sl.shapes.add_textbox(PIn(.44),PIn(.18),PIn(1.3),PIn(.25));tx.text_frame.text='[LOGO]';tx.text_frame.paragraphs[0].font.size=PPt(9);tx.text_frame.paragraphs[0].font.color.rgb=white
    tx=sl.shapes.add_textbox(PIn(.44),PIn(1.4),PIn(8.8),PIn(.95));tx.text_frame.text='研究报告标题';p=tx.text_frame.paragraphs[0];p.font.name='Microsoft YaHei';p.font.size=PPt(30);p.font.bold=True;p.font.color.rgb=white
    tx=sl.shapes.add_textbox(PIn(.46),PIn(2.55),PIn(8.5),PIn(.6));tx.text_frame.text='核心结论 / 决策问题';p=tx.text_frame.paragraphs[0];p.font.name='Microsoft YaHei';p.font.size=PPt(18);p.font.color.rgb=white
    tx=sl.shapes.add_textbox(PIn(.46),PIn(5.1),PIn(8.5),PIn(.25));tx.text_frame.text='日期 · 资料级别';tx.text_frame.paragraphs[0].font.color.rgb=white
    # Executive conclusion
    sl=ppt.slides.add_slide(ppt.slide_layouts[6]);sl.background.fill.solid();sl.background.fill.fore_color.rgb=white
    for label,y,size,col,bold in [('章节名称',.18,9,muted,False),('结论标题：一句话表达决策含义',.52,22,dark,True)]:
        tx=sl.shapes.add_textbox(PIn(.44),PIn(y),PIn(9.0),PIn(.42));tx.text_frame.text=label;p=tx.text_frame.paragraphs[0];p.font.name='Microsoft YaHei';p.font.size=PPt(size);p.font.color.rgb=col;p.font.bold=bold
    rule=sl.shapes.add_shape(MSO_SHAPE.RECTANGLE,PIn(.44),PIn(1.05),PIn(.42),PIn(.045));rule.fill.solid();rule.fill.fore_color.rgb=accent;rule.line.fill.background()
    tx=sl.shapes.add_textbox(PIn(.55),PIn(1.45),PIn(8.7),PIn(1.1));tx.text_frame.text='主要证据与推理';tx.text_frame.paragraphs[0].font.name='Microsoft YaHei';tx.text_frame.paragraphs[0].font.size=PPt(16);tx.text_frame.paragraphs[0].font.color.rgb=dark
    tx=sl.shapes.add_textbox(PIn(.55),PIn(2.8),PIn(8.7),PIn(1.2));tx.text_frame.text='决策含义 / 行动';tx.text_frame.paragraphs[0].font.name='Microsoft YaHei';tx.text_frame.paragraphs[0].font.size=PPt(18);tx.text_frame.paragraphs[0].font.bold=True;tx.text_frame.paragraphs[0].font.color.rgb=accent
    tx=sl.shapes.add_textbox(PIn(.44),PIn(5.25),PIn(8.7),PIn(.2));tx.text_frame.text='来源： [S-01]';tx.text_frame.paragraphs[0].font.size=PPt(7);tx.text_frame.paragraphs[0].font.color.rgb=muted
    # Native editable chart layout
    sl=ppt.slides.add_slide(ppt.slide_layouts[6]);sl.background.fill.solid();sl.background.fill.fore_color.rgb=white
    tx=sl.shapes.add_textbox(PIn(.44),PIn(.18),PIn(9.0),PIn(.35));tx.text_frame.text='时间趋势 / 企业比较';tx.text_frame.paragraphs[0].font.size=PPt(22);tx.text_frame.paragraphs[0].font.bold=True;tx.text_frame.paragraphs[0].font.color.rgb=dark
    data=CategoryChartData();data.categories=['A','B','C'];data.add_series('指标',[12,18,16]);ch=sl.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED,PIn(.55),PIn(1.0),PIn(8.5),PIn(3.8),data).chart;ch.has_legend=False;ch.has_title=False
    ch.series[0].format.fill.solid();ch.series[0].format.fill.fore_color.rgb=accent
    tx=sl.shapes.add_textbox(PIn(.55),PIn(4.95),PIn(8.5),PIn(.28));tx.text_frame.text='单位：示例单位  |  数据来源：[S-01]';tx.text_frame.paragraphs[0].font.size=PPt(8);tx.text_frame.paragraphs[0].font.color.rgb=muted
    # Native editable comparison table layout
    sl=ppt.slides.add_slide(ppt.slide_layouts[6]);sl.background.fill.solid();sl.background.fill.fore_color.rgb=white
    tx=sl.shapes.add_textbox(PIn(.44),PIn(.18),PIn(9.0),PIn(.35));tx.text_frame.text='公司 / 方案比较';tx.text_frame.paragraphs[0].font.size=PPt(22);tx.text_frame.paragraphs[0].font.bold=True;tx.text_frame.paragraphs[0].font.color.rgb=dark
    table=sl.shapes.add_table(3,3,PIn(.5),PIn(1.15),PIn(8.7),PIn(2.4)).table
    for ri,row in enumerate([['比较维度','对象A','对象B'],['产品/能力','输入数据','输入数据'],['证据与限制','[S-01]','[S-02]']]):
        for ci,val in enumerate(row):
            cell=table.cell(ri,ci);cell.text=val;cell.fill.solid();cell.fill.fore_color.rgb=dark if ri==0 else (light if ri%2 else white)
            for p in cell.text_frame.paragraphs:
                p.font.name='Microsoft YaHei';p.font.size=PPt(12);p.font.bold=ri==0;p.font.color.rgb=white if ri==0 else dark
    tx=sl.shapes.add_textbox(PIn(.5),PIn(3.85),PIn(8.7),PIn(.65));tx.text_frame.text='结论与决策含义';tx.text_frame.paragraphs[0].font.name='Microsoft YaHei';tx.text_frame.paragraphs[0].font.size=PPt(16);tx.text_frame.paragraphs[0].font.bold=True;tx.text_frame.paragraphs[0].font.color.rgb=accent
    ppt.save(ROOT/'templates/pptx/research_presentation.pptx')

if __name__=='__main__':
    build_docx();build_pptx();print('DOCX and PPTX templates written')
