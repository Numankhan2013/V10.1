#!/usr/bin/env python3
from pathlib import Path
import json,re,html,sys
import fitz

ROOT=Path('app/src/main'); ASSETS=ROOT/'assets'; OUT=ASSETS/'source_visual_metadata.js'
SUBJECTS={'Anatomy':'Anatomy_QBank_Source.pdf','Physiology':'Physiology_QBank_Source.pdf','Biochemistry':'Biochemistry_QBank_Source.pdf'}
QSTART=re.compile(r'(?m)^\s*(\d{1,4})[.)]\s+')
OPTION=re.compile(r'(?m)^\s*[A-E][.)]\s+')
CUES=re.compile(r'\b(image|figure|fig\.?|shown|shown below|given below|provided|marked|histolog|radiograph|x[- ]?ray|ecg|graph|curve|diagram|illustrat|slide|section|microscop|identify)\b',re.I)

def norm(s):
    s=html.unescape(str(s or '')).lower().replace('\u00ad','')
    s=re.sub(r'[^a-z0-9%°μ×÷+\-./ ]',' ',s)
    return re.sub(r'\s+',' ',s).strip()

def crop_box(page,b):
    r=fitz.Rect(b); pr=page.rect
    if r.get_area()<=100:return None
    m=max(6,min(18,.025*max(r.width,r.height)))
    r=fitz.Rect(max(pr.x0,r.x0-m),max(pr.y0,r.y0-m),min(pr.x1,r.x1+m),min(pr.y1,r.y1+m))
    return {'left':round(r.x0,2),'top':round(r.y0,2),'right':round(r.x1,2),'bottom':round(r.y1,2)}

def visual_boxes(page,txt):
    boxes=[]
    try:
        for b in page.get_text('dict').get('blocks',[]):
            if b.get('type')==1 and b.get('bbox'):
                c=crop_box(page,b['bbox'])
                if c: boxes.append((fitz.Rect(b['bbox']),c))
    except Exception: pass
    if boxes:return boxes
    if not CUES.search(txt):return []
    # Vector fallback only on pages with explicit visual language.
    try:
        rs=[]
        for d in page.get_drawings():
            r=fitz.Rect(d['rect']) if d.get('rect') else None
            if r and r.get_area()>150:rs.append(r)
        if rs:
            u=rs[0]
            for r in rs[1:]:u|=r
            if u.get_area()>page.rect.get_area()*.04:
                c=crop_box(page,u)
                return [(u,c)] if c else []
    except Exception: pass
    return []

def question_segments(page):
    # Parse actual question stems from the source page itself. This is the key
    # invariant: a visual is attached only to the question occupying the same
    # source-PDF region, never to an arbitrary nearest/fuzzy question.
    blocks=[]
    try:
        for b in page.get_text('blocks'):
            if len(b)>=5 and b[4]: blocks.append((float(b[1]),float(b[3]),str(b[4])))
    except Exception:return []
    blocks.sort()
    out=[]
    for y0,y1,text in blocks:
        matches=list(QSTART.finditer(text))
        for j,m in enumerate(matches):
            start=m.start(); end=matches[j+1].start() if j+1<len(matches) else len(text)
            seg=text[start:end]
            stem=OPTION.split(seg,1)[0]
            stem=QSTART.sub('',stem,1).strip()
            if len(norm(stem))<20:continue
            # Approximate the question's vertical span within this text block.
            before=text[:start]; after=text[:end]
            line_count_before=before.count('\n'); line_count_after=after.count('\n')
            total=max(1,text.count('\n')+1); line_h=max(8,(y1-y0)/total)
            sy=y0+line_count_before*line_h
            ey=y1 if j+1==len(matches) else sy+max(line_h,(text[m.end():matches[j+1].start()].count('\n')+1)*line_h)
            out.append((sy,ey,stem))
    return out

def main():
    allmeta={}
    total=0
    for subject,fn in SUBJECTS.items():
        pdf=ASSETS/fn
        if not pdf.exists():print('missing',pdf,file=sys.stderr);sys.exit(1)
        doc=fitz.open(pdf); entries=[]
        for pno,page in enumerate(doc,1):
            txt=page.get_text('text') or ''
            qs=question_segments(page)
            if not qs:continue
            vbs=visual_boxes(page,txt)
            if not vbs:continue
            for sy,ey,stem in qs:
                # A visual belongs to this question only when its center is in
                # that question's vertical source-PDF band. This prevents Q9
                # from inheriting Q7/Q8's graph, and prevents cross-subject bleed.
                candidates=[(abs(((b.y0+b.y1)/2)-sy),c) for b,c in vbs if sy-12 <= (b.y0+b.y1)/2 <= ey+12]
                if not candidates:continue
                _,crop=min(candidates,key=lambda z:z[0])
                entries.append({'match':stem,'visual':{'type':'source-pdf','source':fn,'page':pno,'crop':crop,'fit':'contain','scale':4.0}})
                total+=1
        allmeta[subject]=entries
        print(subject,'pages',doc.page_count,'question visuals',len(entries))
        doc.close()
    OUT.write_text('/* Generated V11 source visual metadata. Exact source-PDF question stems; no fuzzy or question-number assignment. */\nwindow.SOURCE_VISUALS='+json.dumps(allmeta,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf-8')
    print('wrote',OUT,'total',total)
if __name__=='__main__':main()
