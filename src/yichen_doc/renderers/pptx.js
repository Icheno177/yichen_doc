const fs = require('fs');
const path = require('path');
const pptxgen = require('pptxgenjs');

const [contentPath, outputPath] = process.argv.slice(2);
if (!contentPath || !outputPath) throw new Error('Usage: node pptx.js content.json output.pptx');
const content = JSON.parse(fs.readFileSync(contentPath, 'utf8'));
const pptx = new pptxgen();
pptx.layout = 'LAYOUT_WIDE';
pptx.author = content.metadata.author || 'yichen_doc';
pptx.subject = content.decision.question;
pptx.title = content.metadata.title;
pptx.company = 'yichen_doc';
pptx.lang = content.metadata.language || 'zh-CN';
pptx.theme = { headFontFace: 'Microsoft YaHei', bodyFontFace: 'Microsoft YaHei', lang: pptx.lang };
const C = { bg: 'FFFFFF', ink: '202124', gray: '5E6268', red: 'A92332', line: 'D7DADD', pale: 'F2F3F4' };
let n = 0;
function base(title, eyebrow='研究内容') {
  const s = pptx.addSlide(); n++;
  s.background = { color: C.bg };
  s.addText(eyebrow, { x:.55, y:.22, w:11.8, h:.24, fontFace:'Microsoft YaHei', fontSize:10, color:C.gray, margin:0 });
  s.addText(title, { x:.55, y:.72, w:12.1, h:.65, fontFace:'Microsoft YaHei', fontSize:25, bold:true, color:C.ink, margin:0, breakLine:false, fit:'shrink' });
  s.addShape(pptx.ShapeType.line, { x:.55, y:1.53, w:12.22, h:0, line:{color:C.line,width:1} });
  s.addShape(pptx.ShapeType.rect, { x:.55, y:1.51, w:.52, h:.045, line:{color:C.red,transparency:100}, fill:{color:C.red} });
  s.addText(`${n}`, { x:12.15, y:7.14, w:.5, h:.2, fontFace:'Microsoft YaHei', fontSize:9, color:C.gray, align:'right', margin:0 });
  return s;
}
function table(slide, block, x=.62, y=2.0, w=12.0, h=4.55) {
  const rows = [block.headers, ...(block.rows || [])].map((row, ri) => row.map(v => ({text:String(v ?? ''), options:{bold:ri===0,color:ri===0?'FFFFFF':C.ink,fill:ri===0?C.ink:(ri%2===0?C.pale:C.bg),fontFace:'Microsoft YaHei',fontSize:ri===0?12:11,breakLine:false}})));
  slide.addTable(rows, { x,y,w,h, border:{type:'solid',color:C.line,pt:.5}, margin:.08, rowH:.36, autoFit:false });
}
function chart(slide,b) {
  const types = {bar:pptx.ChartType.bar,line:pptx.ChartType.line,pie:pptx.ChartType.pie,scatter:pptx.ChartType.scatter,stacked_bar:pptx.ChartType.bar};
  const data = b.chart_type==='scatter'
    ? b.series.map(s => ({name:s.name,values:b.x_values.map((x,i)=>({x,y:s.values[i]}))}))
    : b.series.map(s => ({name:s.name,labels:b.categories,values:s.values}));
  slide.addChart(types[b.chart_type] || pptx.ChartType.bar, data, {x:.75,y:2.05,w:11.8,h:4.35,catAxisLabelFontFace:'Microsoft YaHei',catAxisLabelFontSize:12,valAxisLabelFontFace:'Microsoft YaHei',valAxisLabelFontSize:10,valAxisTitle:b.unit||'',showTitle:false,showLegend:data.length>1,showValue:true,showCatName:false,showValAxisTitle:!!b.unit,showCatAxisTitle:false,showMarker:b.chart_type==='line',chartColors:[C.red,'9BA0A6',C.ink],showSerName:false,showGridLines:true,showValAxis:true,showCatAxisLabel:true,showValAxisLabel:true,grouping:b.chart_type==='stacked_bar'?'stacked':'clustered',valAxisMinVal:0,valGridLine:{color:'D7DADD',width:.5,style:'solid'}});
}
function addBlock(slide,b) {
  if (b.type==='heading') slide.addText(b.text||'',{x:.7,y:1.9,w:11.8,h:.4,fontFace:'Microsoft YaHei',fontSize:17,bold:true,color:C.red,margin:0});
  else if (b.type==='paragraph'||b.type==='callout'||b.type==='formula'||b.type==='citation') slide.addText([{text:(b.label?`${b.label}  `:''),options:{bold:true,color:C.red}},{text:b.text||b.formula||'',options:{color:C.ink}}],{x:.72,y:2.0,w:11.8,h:1.25,fontFace:'Microsoft YaHei',fontSize:16,breakLine:false,fit:'shrink',valign:'mid',margin:.06,paraSpaceAfterPt:6});
  else if (b.type==='metric') {
    slide.addShape(pptx.ShapeType.roundRect,{x:.8,y:2.2,w:3.3,h:2.0,rectRadius:.08,line:{color:C.line,pt:1},fill:{color:'FAFAFA'}});
    slide.addText(b.label||'',{x:1,y:2.48,w:2.9,h:.3,fontFace:'Microsoft YaHei',fontSize:13,color:C.gray,margin:0});
    slide.addText(`${b.value??''} ${b.unit||''}`,{x:1,y:2.95,w:2.9,h:.75,fontFace:'Microsoft YaHei',fontSize:27,bold:true,color:C.red,margin:0,fit:'shrink'});
  }
  else if (b.type==='table') table(slide,b);
  else if (b.type==='chart') chart(slide,b);
  else if (b.type==='image') {
    const img=path.resolve(path.dirname(contentPath),b.image_path);
    if (!fs.existsSync(img)) throw new Error(`Image not found: ${img}`);
    slide.addImage({path:img,x:1.0,y:1.95,w:11.2,h:4.6,sizing:'contain',altText:b.alt||'Research image'});
    if (b.alt) slide.addText(b.alt,{x:1,y:6.58,w:11.2,h:.25,fontFace:'Microsoft YaHei',fontSize:9,color:C.gray,align:'center',margin:0});
  }
}

// Cover
{
 const s=pptx.addSlide(); n++; s.background={color:C.ink};
 if (content.metadata.logo_path) {
   const logo=path.resolve(path.dirname(contentPath),content.metadata.logo_path);
   if (!fs.existsSync(logo)) throw new Error(`Logo not found: ${logo}`);
   s.addImage({path:logo,x:.72,y:.42,w:1.25,h:.62,sizing:'contain',altText:'Organization logo'});
 }
 if (content.metadata.cover_image_path) {
   const cover=path.resolve(path.dirname(contentPath),content.metadata.cover_image_path);
   if (!fs.existsSync(cover)) throw new Error(`Cover image not found: ${cover}`);
   s.addImage({path:cover,x:8.25,y:1.05,w:4.35,h:4.85,sizing:'contain',altText:'Cover concept image'});
 }
 s.addShape(pptx.ShapeType.rect,{x:.68,y:.72,w:.62,h:.08,line:{color:C.red,transparency:100},fill:{color:C.red}});
 s.addText(content.metadata.date||'',{x:.7,y:1.15,w:5.6,h:.5,fontFace:'Microsoft YaHei',fontSize:20,color:'C7C9CD',margin:0});
 s.addText(content.metadata.title,{x:.7,y:2.0,w:11.8,h:1.15,fontFace:'Microsoft YaHei',fontSize:34,bold:true,color:'FFFFFF',fit:'shrink',margin:0});
 s.addText(content.decision.question,{x:.72,y:3.45,w:11.6,h:.8,fontFace:'Microsoft YaHei',fontSize:20,color:'FFFFFF',fit:'shrink',margin:0});
 s.addText(content.metadata.confidentiality||'yichen_doc',{x:.72,y:6.95,w:11,h:.25,fontFace:'Microsoft YaHei',fontSize:10,color:'D7DADD',margin:0});
}
// Executive decision slide
{
 const s=base('决策摘要','决策问题');
 s.addText(content.decision.question,{x:.72,y:2.0,w:11.8,h:.5,fontFace:'Microsoft YaHei',fontSize:18,bold:true,color:C.ink,margin:0,fit:'shrink'});
 s.addShape(pptx.ShapeType.roundRect,{x:.72,y:2.8,w:11.8,h:2.0,line:{color:C.line,pt:1},fill:{color:'FAFAFA'}});
 s.addText(content.decision.answer,{x:1.0,y:3.08,w:11.2,h:1.45,fontFace:'Microsoft YaHei',fontSize:18,color:C.ink,fit:'shrink',valign:'mid',margin:.05});
}
for (const sec of content.sections) {
 const intro=base(sec.title, '研究内容');
 if (sec.conclusion) intro.addText(sec.conclusion,{x:.72,y:2.05,w:11.8,h:1.45,fontFace:'Microsoft YaHei',fontSize:20,bold:true,color:C.ink,margin:.04,fit:'shrink',valign:'mid'});
 for (const b of sec.blocks) {
   const label=b.label || b.text || b.type;
   const slide=base(sec.title, label.slice(0,72));
   if (sec.conclusion) slide.addText(sec.conclusion,{x:.68,y:1.68,w:11.9,h:.34,fontFace:'Microsoft YaHei',fontSize:12,bold:true,color:C.gray,margin:0,fit:'shrink'});
   if (b.type==='table'||b.type==='chart'||b.type==='image') addBlock(slide,b);
   else if (b.type==='metric') addBlock(slide,b);
   else if (b.type==='heading') slide.addText(b.text||'',{x:.75,y:2.2,w:11.8,h:.72,fontFace:'Microsoft YaHei',fontSize:24,bold:true,color:C.red,margin:.04,fit:'shrink'});
   else slide.addText([{text:(b.label?`${b.label}  `:''),options:{bold:true,color:C.red}},{text:b.text||b.formula||'',options:{color:C.ink}}],{x:.78,y:2.22,w:11.65,h:2.4,fontFace:'Microsoft YaHei',fontSize:20,fit:'shrink',breakLine:false,margin:.08,valign:'mid'});
   const unique=[...new Set(b.source_ids||[])];
   if (unique.length) slide.addText('来源：'+unique.join('、'),{x:.65,y:6.7,w:11.4,h:.28,fontFace:'Microsoft YaHei',fontSize:8,color:C.gray,margin:0,fit:'shrink'});
 }
}
const out=path.resolve(outputPath); fs.mkdirSync(path.dirname(out),{recursive:true});
pptx.writeFile({fileName:out}).then(()=>process.exit(0)).catch(err=>{console.error(err);process.exit(1)});
