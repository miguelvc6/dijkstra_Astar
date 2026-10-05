"""Print-friendly PDFs from the editable Markdown handouts (no font redistribution)."""
from __future__ import annotations
from pathlib import Path
import re
from html import escape
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, Image, Preformatted
from reportlab.pdfbase import pdfmetrics
from .make_slides import REG, BOLD, MONO

INK=colors.HexColor('#17323d'); TEAL=colors.HexColor('#087e79')

def inline(s):
    s=escape(s)
    # Protect code, then transform links and emphasis. Long URLs remain breakable.
    s=re.sub(r'`([^`]+)`',lambda m:'<font name="'+MONO+'" size="8.4">'+m.group(1)+'</font>',s)
    s=re.sub(r'\[([^\]]+)\]\(([^)]+)\)',r'<link href="\2" color="#087e79">\1</link>',s)
    s=re.sub(r'\*\*([^*]+)\*\*',r'<b>\1</b>',s)
    return s

def make_pdf(source, destination, *, worksheet=False, title=None):
    source=Path(source); destination=Path(destination)
    fs=9.1 if worksheet else 10.1; lead=12.6 if worksheet else 14.2
    pdfmetrics.registerFontFamily(REG,normal=REG,bold=BOLD,italic=REG,boldItalic=BOLD)
    body=ParagraphStyle('body',fontName=REG,fontSize=fs,leading=lead,textColor=INK,spaceAfter=6 if worksheet else 8,splitLongWords=True)
    h1=ParagraphStyle('h1',parent=body,fontName=BOLD,fontSize=21,leading=25,spaceAfter=11,keepWithNext=True)
    h2=ParagraphStyle('h2',parent=body,fontName=BOLD,fontSize=12.6,leading=16,spaceBefore=8,spaceAfter=7,keepWithNext=True,textColor=TEAL)
    h3=ParagraphStyle('h3',parent=h2,fontSize=11,leading=14)
    cell=ParagraphStyle('cell',parent=body,fontSize=8.5 if worksheet else 9,leading=11.5,spaceAfter=0)
    code=ParagraphStyle('code',fontName=MONO,fontSize=7.5 if worksheet else 8.3,leading=11.3,textColor=INK,backColor=colors.HexColor('#edf1ed'),borderPadding=8,spaceBefore=4,spaceAfter=10)
    title=title or source.stem.replace('_',' ').title()
    width=A4[0]-88
    doc=SimpleDocTemplate(str(destination),pagesize=A4,leftMargin=44,rightMargin=44,topMargin=43,bottomMargin=43,title=title,author='Pathfinding lecture teaching package')
    story=[];lines=source.read_text().splitlines();i=0
    while i<len(lines):
        line=lines[i].strip()
        if not line:i+=1;continue
        if '<!-- PAGEBREAK -->' in line:story.append(PageBreak());i+=1;continue
        if line.startswith('```'):
            i+=1;chunk=[]
            while i<len(lines) and not lines[i].startswith('```'):chunk.append(lines[i]);i+=1
            story.append(Preformatted('\n'.join(chunk),code,maxLineLength=100));i+=1;continue
        if line.startswith('|'):
            rows=[]
            while i<len(lines) and lines[i].strip().startswith('|'):
                fields=[c.strip() for c in lines[i].strip().strip('|').split('|')]
                if not all(re.fullmatch(r':?-+:?',c.replace(' ','')) for c in fields):rows.append(fields)
                i+=1
            n=len(rows[0]); widths=[width/n]*n
            if worksheet and n==2:widths=[width*.30,width*.70]
            elif worksheet and n==5:widths=[width*.23,width*.09,width*.09,width*.09,width*.5]
            elif n==3:widths=[width*.22,width*.39,width*.39]
            vals=[[Paragraph(inline(c or ' '),cell) for c in row] for row in rows]
            t=Table(vals,colWidths=widths,repeatRows=1,hAlign='LEFT')
            t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e3ece7')),('VALIGN',(0,0),(-1,-1),'TOP'),('LINEBELOW',(0,0),(-1,0),.8,TEAL),('LINEBELOW',(0,1),(-1,-1),.35,colors.HexColor('#cbd5d1')),('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),7 if worksheet else 6),('BOTTOMPADDING',(0,0),(-1,-1),8 if worksheet else 6)]))
            story.extend([t,Spacer(1,9)]);continue
        image=re.fullmatch(r'!\[([^\]]*)\]\(([^)]+)\)',line)
        if image:
            p=(source.parent/image.group(2)).resolve()
            from PIL import Image as PILImage
            with PILImage.open(p) as im:iw,ih=im.size
            w=min(width,370 if worksheet else width);h=w*ih/iw
            story.extend([Image(str(p),width=w,height=h,hAlign='CENTER'),Spacer(1,6)]);i+=1;continue
        if line.startswith('# '):story.append(Paragraph(inline(line[2:]),h1));i+=1;continue
        if line.startswith('## '):story.append(Paragraph(inline(line[3:]),h2));i+=1;continue
        if line.startswith('### '):story.append(Paragraph(inline(line[4:]),h3));i+=1;continue
        if line.startswith('---'):story.append(Spacer(1,8));i+=1;continue
        chunk=[line];i+=1
        while i<len(lines) and lines[i].strip() and not lines[i].startswith(('#','|','```','![','<!--','- ')) and not re.match(r'^\d+\. ',lines[i]):chunk.append(lines[i].strip());i+=1
        text=' '.join(chunk)
        if re.match(r'^_{10}',text):
            # A writing line, not a long unbreakable underscore run.
            t=Table([['']],colWidths=[width],rowHeights=[12]);t.setStyle(TableStyle([('LINEBELOW',(0,0),(-1,-1),.4,colors.HexColor('#b1bfbc'))]));story.extend([t,Spacer(1,6)])
        else:story.append(Paragraph(inline(text),body))
    def decorate(c,d):
        c.saveState();c.setStrokeColor(TEAL);c.setLineWidth(.7);c.line(44,A4[1]-29,A4[0]-44,A4[1]-29)
        c.setFont(REG,7.3);c.setFillColor(INK);c.drawString(44,23,'DIJKSTRA + A*  /  '+title.upper());c.drawRightString(A4[0]-44,23,str(d.page));c.restoreState()
    doc.build(story,onFirstPage=decorate,onLaterPages=decorate)
    return destination

def build(root):
    root=Path(root)
    for name,title in [('teacher_guide','Teacher guide'),('student_worksheet','Student worksheet'),('worksheet_solutions','Worksheet solutions')]:
        make_pdf(root/f'handouts/{name}.md',root/f'handouts/{name}.pdf',worksheet=name=='student_worksheet',title=title)
    make_pdf(root/'docs/references.md',root/'handouts/reference_sheet.pdf',title='References and provenance')
    make_pdf(root/'docs/technical_notes.md',root/'handouts/technical_notes.pdf',title='Technical notes')

if __name__=='__main__':build(Path(__file__).resolve().parents[1])
