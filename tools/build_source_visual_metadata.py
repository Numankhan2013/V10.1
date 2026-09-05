#!/usr/bin/env python3
from pathlib import Path
import json,re,html,sys
import fitz

ROOT=Path('app/src/main')
ASSETS=ROOT/'assets'
OUT=ASSETS/'source_visual_metadata.js'
SUBJECTS={'Anatomy':'Anatomy_QBank_Source.pdf','Physiology':'Physiology_QBank_Source.pdf','Biochemistry':'Biochemistry_QBank_Source.pdf'}

def norm(s):
    s=html.unescape(str(s or '')).lower()
    s=re.sub(r'[^a-z0-9%°μ×÷+\-./ ?]',' ',s)
    return re.sub(r'\s+',' ',s).strip()

def page_visual(page):
    rect=page.rect; boxes=[]
    try:
        for info in page.get_image_info():
            b=fitz.Rect(info['bbox'])
            if b.get_area()>100: boxes.append(b)
    except Exception: pass
    if boxes:
        b=max(boxes,key=lambda x:x.get_area())
        margin=max(6,min(18,0.025*max(b.width,b.height)))
        b=fitz.Rect(max(rect.x0,b.x0-margin),max(rect.y0,b.y0-margin),min(rect.x1,b.x1+margin),min(rect.y1,b.y1+margin))
        return {'left':round(b.x0,2),'top':round(b.y0,2),'right':round(b.x1,2),'bottom':round(b.y1,2)}
    try:
        rs=[]
        for d in page.get_drawings():
            if d.get('rect'):
                r=fitz.Rect(d['rect'])
                if r.get_area()>150: rs.append(r)
        if rs:
            u=rs[0]
            for r in rs[1:]: u|=r
            if u.get_area()>rect.get_area()*0.04:
                m=8; u=fitz.Rect(max(rect.x0,u.x0-m),max(rect.y0,u.y0-m),min(rect.x1,u.x1+m),min(rect.y1,u.y1+m))
                return {'left':round(u.x0,2),'top':round(u.y0,2),'right':round(u.x1,2),'bottom':round(u.y1,2)}
    except Exception: pass
    return None

def question_like(txt):
    n=norm(txt)
    if len(n)<35:return False
    return '?' in n or bool(re.search(r'\b[a-d][.)]\s',n))

def main():
    allmeta={}
    for subject,fn in SUBJECTS.items():
        pdf=ASSETS/fn
        if not pdf.exists(): print('missing',pdf,file=sys.stderr);sys.exit(1)
        doc=fitz.open(pdf); entries=[]
        for i,page in enumerate(doc):
            txt=page.get_text('text') or ''
            if not question_like(txt): continue
            vis=page_visual(page)
            if not vis: continue
            lines=[x.strip() for x in txt.splitlines() if x.strip()]
            fingerprint=' '.join(lines[:18])[:700]
            entries.append({'match':fingerprint,'visual':{'type':'source-pdf','source':fn,'page':i+1,'crop':vis,'fit':'contain','scale':2.5}})
        allmeta[subject]=entries
        print(subject,'pages',doc.page_count,'visual question-page candidates',len(entries))
        doc.close()
    OUT.write_text('/* Generated V11 source visual metadata. Subject-local text fingerprints; no question-number heuristics. */\nwindow.SOURCE_VISUALS='+json.dumps(allmeta,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf-8')
    print('wrote',OUT)
if __name__=='__main__':main()
