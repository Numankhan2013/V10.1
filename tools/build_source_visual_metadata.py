#!/usr/bin/env python3
from pathlib import Path
import json,re,html,sys
import fitz

ROOT=Path('app/src/main')
ASSETS=ROOT/'assets'
OUT=ASSETS/'source_visual_metadata.js'
SUBJECTS={'Anatomy':'Anatomy_QBank_Source.pdf','Physiology':'Physiology_QBank_Source.pdf','Biochemistry':'Biochemistry_QBank_Source.pdf'}

KEY_RE=re.compile(r'''(?:["'](?:question|questionText|stem|question_text|text)["']\s*:\s*["'])(.*?)(?<!\\)["']''',re.I|re.S)

def js_unescape(s):
    try:return bytes(s,'utf-8').decode('unicode_escape')
    except Exception:return s

def norm(s):
    s=html.unescape(str(s or '')).lower()
    s=re.sub(r'\\["\'\\/]','',s)
    s=re.sub(r'[^a-z0-9%°μ×÷+\-./ ]',' ',s)
    return re.sub(r'\s+',' ',s).strip()

def extract_questions():
    texts=[]
    for fn in ['subjects_qbank_data.js','qbank_data.js','index.html']:
        p=ASSETS/fn
        if not p.exists():continue
        raw=p.read_text(encoding='utf-8',errors='ignore')
        for m in KEY_RE.finditer(raw):
            q=js_unescape(m.group(1)).strip()
            n=norm(q)
            if 20<=len(n)<=700 and len(n.split())>=5:
                texts.append(q)
    seen=set(); out=[]
    for q in texts:
        n=norm(q)
        if n not in seen: seen.add(n); out.append(q)
    return out

def page_visual(page):
    rect=page.rect
    boxes=[]
    try:
        for info in page.get_image_info():
            b=fitz.Rect(info['bbox'])
            if b.get_area()>100: boxes.append(b)
    except Exception: pass
    if boxes:
        # Prefer the largest meaningful image, with a small safety margin.
        b=max(boxes,key=lambda x:x.get_area())
        margin=max(6,min(18,0.025*max(b.width,b.height)))
        b=fitz.Rect(max(rect.x0,b.x0-margin),max(rect.y0,b.y0-margin),min(rect.x1,b.x1+margin),min(rect.y1,b.y1+margin))
        return {'left':round(b.x0,2),'top':round(b.y0,2),'right':round(b.x1,2),'bottom':round(b.y1,2)}
    # Vector diagrams/tables: use drawing union only when it is substantial.
    try:
        ds=page.get_drawings()
        rs=[fitz.Rect(d['rect']) for d in ds if d.get('rect') and fitz.Rect(d['rect']).get_area()>150]
        if rs:
            u=rs[0]
            for r in rs[1:]: u|=r
            if u.get_area()>rect.get_area()*0.04:
                m=8; u=fitz.Rect(max(rect.x0,u.x0-m),max(rect.y0,u.y0-m),min(rect.x1,u.x1+m),min(rect.y1,u.y1+m))
                return {'left':round(u.x0,2),'top':round(u.y0,2),'right':round(u.x1,2),'bottom':round(u.y1,2)}
    except Exception: pass
    return None

def best_page(doc,q):
    nq=norm(q)
    if not nq:return None
    qwords=[w for w in nq.split() if len(w)>=4][:24]
    if not qwords:return None
    best=None; bestscore=0
    for i,p in enumerate(doc):
        txt=norm(p.get_text('text'))
        if not txt:continue
        # Strong exact-prefix signal, then token overlap.
        score=0
        prefix=' '.join(qwords[:10])
        if prefix and prefix in txt: score=100
        else:
            hits=sum(1 for w in qwords if w in txt)
            score=hits/len(qwords)
        if score>bestscore:
            bestscore=score; best=i
            if score>=100:break
    if best is None or bestscore<0.55:return None
    vis=page_visual(doc[best])
    if not vis:return None
    return best+1,vis,bestscore

def main():
    questions=extract_questions()
    print('SOURCE VISUAL: extracted question-like strings:',len(questions))
    allmeta={}
    for subject,fn in SUBJECTS.items():
        pdf=ASSETS/fn
        if not pdf.exists():
            print('missing',pdf,file=sys.stderr); sys.exit(1)
        doc=fitz.open(pdf); entries=[]; seen=set(); matched=0
        for idx,q in enumerate(questions):
            r=best_page(doc,q)
            if not r:continue
            page,crop,sc=r; key=norm(q)
            if key in seen:continue
            seen.add(key); matched+=1
            entries.append({'match':q,'visual':{'type':'source-pdf','source':fn,'page':page,'crop':crop,'fit':'contain','scale':2.5}})
        allmeta[subject]=entries
        print(subject,'pages',doc.page_count,'visual matches',matched)
        doc.close()
    OUT.write_text('/* Generated V11 source visual metadata. Text-keyed; no question-number heuristics. */\nwindow.SOURCE_VISUALS='+json.dumps(allmeta,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf-8')
    print('wrote',OUT)
if __name__=='__main__':main()
