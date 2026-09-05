#!/usr/bin/env python3
"""Build deterministic question -> original source-PDF visual metadata.

The QBank JSON supplies authoritative question/source-page boundaries. The
source PDFs supply the original figures. A figure is accepted only when it
lies inside that question's own source-page interval and question band.
There is deliberately no fuzzy text matching, nearest-question guessing,
subject fallback, or solution-page assignment.
"""
from pathlib import Path
import json,re,sys
import fitz

ROOT=Path('app/src/main'); ASSETS=ROOT/'assets'; OUT=ASSETS/'source_visual_metadata.js'
SUBJECTS={
    'Anatomy':('Anatomy_QBank_Source.pdf','subjects_qbank_data.js'),
    'Physiology':('Physiology_QBank_Source.pdf','subjects_qbank_data.js'),
    'Biochemistry':('Biochemistry_QBank_Source.pdf','qbank_data.js'),
}
QSTART=re.compile(r'(?m)^\s*(\d{1,4})[.)]\s+')
VISUAL_CUE=re.compile(r'\b(image|figure|fig\.?|shown|shown below|given below|provided|marked|histolog|radiograph|x[- ]?ray|ecg|graph|curve|diagram|illustrat|slide|section|microscop|identify)\b',re.I)
SOLUTION=re.compile(r'\b(?:solution\s+for\s+question|correct\s+answer\s*:|explanation\s*:)',re.I)
LEAKED_REFERENCE=re.compile(r'\s*\*{0,2}Visual\s*/\s*Image\s*Reference\s*:\s*\*{0,2}.*?(?=\s*$)',re.I|re.S)

def clean_question_text(text):
    """Remove internal extraction/provenance boilerplate from user-facing text.

    Older source-ingestion passes inserted a Visual/Image Reference paragraph
    into some question strings. It is metadata, not question content, and must
    never become visible or participate in exact visual matching.
    """
    s=str(text or '')
    s=LEAKED_REFERENCE.sub('',s)
    return re.sub(r'\s{2,}',' ',s).strip()

def load_questions(file,subject):
    data=json.loads((ASSETS/file).read_text(encoding='utf-8').split('=',1)[1].rstrip(';\n'))
    if subject=='Biochemistry':
        qs=data.get('questions',[])
    else:
        qs=next(s for s in data.get('subjects',[]) if s.get('subject')==subject).get('questions',[])
    for q in qs:
        q['_display_question']=clean_question_text(q.get('question',''))
    return sorted((q for q in qs if q.get('sourcePage')),
                  key=lambda q:(int(q['sourcePage']),int(q.get('questionNumber',0))))

def crop_box(page,bbox):
    """Return a tight, presentation-ready crop around a source figure.

    Image-resource bboxes often contain a large white/pale canvas. Render at
    inspection scale, find the actual non-background content, and crop to it.
    The final crop keeps a small safety margin and never exceeds the source
    image rectangle. This is intentionally independent of the UI card size.
    """
    r=fitz.Rect(bbox); pr=page.rect
    if r.get_area()<=100:return None
    # Small safety border before content detection.
    m=max(2,min(8,.012*max(r.width,r.height)))
    r=fitz.Rect(max(pr.x0,r.x0-m),max(pr.y0,r.y0-m),min(pr.x1,r.x1+m),min(pr.y1,r.y1+m))
    try:
        inspect_scale=2.0
        pix=page.get_pixmap(matrix=fitz.Matrix(inspect_scale,inspect_scale),clip=r,alpha=False)
        w,h=pix.width,pix.height; raw=pix.samples
        minx,miny=w,h; maxx=maxy=-1
        # Detect meaningful content against white/light backgrounds. Include
        # low-saturation dark text and colored/pastel diagrams.
        for yy in range(h):
            row=yy*w*3
            for xx in range(w):
                k=row+xx*3; rr,gg,bb=raw[k],raw[k+1],raw[k+2]
                if min(rr,gg,bb)<238 or max(rr,gg,bb)-min(rr,gg,bb)>10:
                    minx=min(minx,xx); maxx=max(maxx,xx); miny=min(miny,yy); maxy=max(maxy,yy)
        if maxx>=0:
            pad=max(8,int(min(w,h)*0.035))
            x0=max(0,minx-pad); x1=min(w-1,maxx+pad)
            y0=max(0,miny-pad); y1=min(h-1,maxy+pad)
            sx=1/inspect_scale
            tight=fitz.Rect(r.x0+x0*sx,r.y0+y0*sx,r.x0+(x1+1)*sx,r.y0+(y1+1)*sx)
            # Only accept a detected crop when it remains a substantial
            # portion of the figure; this avoids accidentally selecting a
            # stray anti-aliased pixel from an otherwise blank canvas.
            if tight.get_area()>=max(64,r.get_area()*0.03):
                r=tight
    except Exception:
        pass
    return {'left':round(max(pr.x0,r.x0),2),'top':round(max(pr.y0,r.y0),2),'right':round(min(pr.x1,r.x1),2),'bottom':round(min(pr.y1,r.y1),2)}

def page_question_starts(page):
    out=[]
    for b in page.get_text('blocks'):
        text=str(b[4] or '')
        matches=list(QSTART.finditer(text))
        if not matches: continue
        lines=max(1,text.count('\n')+1)
        line_h=max(8.0,(float(b[3])-float(b[1]))/lines)
        for m in matches:
            y=float(b[1])+text[:m.start()].count('\n')*line_h
            out.append((y,int(m.group(1))))
    return sorted(out)

def question_end_pages(qs,subject):
    ends={}
    for i,q in enumerate(qs):
        end=int(q.get('sourcePageEnd') or q['sourcePage'])
        if subject=='Biochemistry':
            nxt=qs[i+1] if i+1<len(qs) else None
            if nxt is None or nxt.get('chapterId')!=q.get('chapterId'):
                end=int(q['sourcePage'])
        ends[q['id']]=max(int(q['sourcePage']),end)
    return ends

def main():
    allmeta={}; report={}
    for subject,(pdf_name,data_name) in SUBJECTS.items():
        pdf=ASSETS/pdf_name
        if not pdf.exists():
            print('missing',pdf,file=sys.stderr);sys.exit(1)
        qs=load_questions(data_name,subject)
        if not qs:
            print('no questions for',subject,file=sys.stderr);sys.exit(1)
        ends=question_end_pages(qs,subject)
        starts_by_page={}
        for q in qs:
            starts_by_page.setdefault(int(q['sourcePage']),{}).setdefault(int(q.get('questionNumber',-1)),[]).append(q)
        active_by_page={}
        for q in qs:
            for pg in range(int(q['sourcePage']),ends[q['id']]+1):
                active_by_page.setdefault(pg,[]).append(q)
        doc=fitz.open(pdf); assigned={}; pages_with_visuals=0; image_blocks=0
        for pno in sorted(active_by_page):
            page=doc[pno-1]
            txt=page.get_text('text') or ''
            if SOLUTION.search(txt): continue
            cands=active_by_page[pno]
            starts=page_question_starts(page)
            blocks=[b for b in page.get_text('dict').get('blocks',[]) if b.get('type')==1 and b.get('bbox')]
            if not blocks: continue
            valid=[]
            for b in blocks:
                r=fitz.Rect(b['bbox'])
                if r.get_area()<=100: continue
                cy=(r.y0+r.y1)/2; owner=None
                # Prefer the printed question boundary on the same page.
                for y,n in starts:
                    if y>cy: break
                    for q in starts_by_page.get(pno,{}).get(n,[]):
                        if q in cands: owner=q
                # If the source question starts on an earlier page, keep the
                # figure only within that question's explicit source interval.
                if owner is None:
                    prev=[q for q in cands if int(q['sourcePage'])<pno]
                    if prev: owner=max(prev,key=lambda q:int(q['sourcePage']))
                if owner is None: continue
                if not (int(owner['sourcePage'])<=pno<=ends[owner['id']]): continue
                crop=crop_box(page,b['bbox'])
                if crop:
                    valid.append((owner,r.get_area(),{'type':'source-pdf','source':pdf_name,'page':pno,'crop':crop,'fit':'contain','scale':4.0}))
            if valid:
                pages_with_visuals+=1; image_blocks+=len(valid)
                for owner,area,visual in valid:
                    assigned.setdefault(owner['id'],[]).append((area,visual))
        entries=[]; cue_total=0; cue_mapped=0
        for q in qs:
            question_text=q.get('_display_question','')
            cue=bool(VISUAL_CUE.search(question_text))
            if cue: cue_total+=1
            vals=sorted(assigned.get(q['id'],[]),key=lambda z:z[0],reverse=True)
            if not vals: continue
            if cue: cue_mapped+=1
            visuals=[v for _,v in vals]
            entries.append({'match':question_text,'visual':visuals[0],'visuals':visuals})
        if not entries:
            print(subject,'NO VALID QUESTION VISUALS',file=sys.stderr);sys.exit(1)
        allmeta[subject]=entries
        report[subject]={
            'questions':len(qs),'mappedQuestions':len(entries),
            'cueQuestions':cue_total,'cueMapped':cue_mapped,
            'pagesWithVisuals':pages_with_visuals,'imageBlocksAccepted':image_blocks,
        }
        print(subject,'pages',doc.page_count,'questions',len(qs),'question visuals',len(entries),'cue mapped',cue_mapped,'/',cue_total)
        doc.close()
    for subject,r in report.items():
        if r['mappedQuestions']<10:
            print('mapping floor failed for',subject,r,file=sys.stderr);sys.exit(1)
    OUT.write_text(
        '/* Generated V11 source visual metadata. Exact QBank-indexed PDF image blocks; no fuzzy assignment. */\n'
        'window.SOURCE_VISUALS='+json.dumps(allmeta,ensure_ascii=False,separators=(',',':'))+';\n',
        encoding='utf-8')
    (ASSETS/'source_visual_mapping_report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print('wrote',OUT,'total',sum(len(v) for v in allmeta.values()))

if __name__=='__main__': main()
