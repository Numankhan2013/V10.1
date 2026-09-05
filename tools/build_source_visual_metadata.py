#!/usr/bin/env python3
"""Deterministic question -> original source-PDF visual metadata."""
from pathlib import Path
import json,re,sys
import fitz
ROOT=Path('app/src/main'); ASSETS=ROOT/'assets'; OUT=ASSETS/'source_visual_metadata.js'
SUBJECTS={'Anatomy':('Anatomy_QBank_Source.pdf','subjects_qbank_data.js'),'Physiology':('Physiology_QBank_Source.pdf','subjects_qbank_data.js'),'Biochemistry':('Biochemistry_QBank_Source.pdf','qbank_data.js')}
QSTART=re.compile(r'(?m)^\s*(\d{1,4})[.)]\s+')
VISUAL_CUE=re.compile(r'\b(image|figure|fig\.?|shown|given below|provided|marked|histolog|radiograph|x[- ]?ray|ecg|graph|curve|diagram|illustrat|slide|section|microscop|identify)\b',re.I)
SOLUTION=re.compile(r'\b(?:solution\s+for\s+question|correct\s+answer\s*:|explanation\s*:)',re.I)
LEAKED_REFERENCE=re.compile(r'\s*\*{0,2}Visual\s*/\s*Image\s*Reference\s*:\s*\*{0,2}.*?(?=\s*$)',re.I|re.S)
def clean_question_text(text):
    s=str(text or '').replace('{{caption_text}}',''); s=LEAKED_REFERENCE.sub('',s); return re.sub(r'\s{2,}',' ',s).strip()
def load_questions(file,subject):
    data=json.loads((ASSETS/file).read_text(encoding='utf-8').split('=',1)[1].rstrip(';\n'))
    qs=data.get('questions',[]) if subject=='Biochemistry' else next(s for s in data.get('subjects',[]) if s.get('subject')==subject).get('questions',[])
    for q in qs:q['_display_question']=clean_question_text(q.get('question',''))
    return sorted((q for q in qs if q.get('sourcePage')),key=lambda q:(int(q['sourcePage']),int(q.get('questionNumber',0))))

def crop_box(page,bbox,xref=None):
    """Crop the actual embedded figure panel, not the PDF screenshot border."""
    r=fitz.Rect(bbox); pr=page.rect
    if r.get_area()<=100:return None
    # Inspect the native embedded image. Many source figures are screenshots
    # with a white outer frame and a pale/coloured inner figure panel. Detect
    # the large light panel directly from native pixels, then map it back to
    # the page rectangle. This removes the page frame without redrawing it.
    if xref:
        try:
            pm=fitz.Pixmap(page.parent,int(xref)); w,h,n=pm.width,pm.height,pm.n
            if w>20 and h>20:
                raw=pm.samples; x0,x1=int(w*.08),int(w*.92); y0,y1=int(h*.08),int(h*.92)
                bins={}; step=max(1,int((w*h)/100000))
                for yy in range(y0,y1,step):
                    row=yy*w*n
                    for xx in range(x0,x1,step):
                        k=row+xx*n; rr,gg,bb=raw[k],raw[k+1],raw[k+2]
                        if min(rr,gg,bb)>=232:
                            key=(int(rr)//4*4,int(gg)//4*4,int(bb)//4*4); bins[key]=bins.get(key,0)+1
                if bins:
                    bg,count=max(bins.items(),key=lambda z:z[1])
                    if count>=(x1-x0)*(y1-y0)//100:
                        bx,by,bz=bg; minx,miny=w,h; maxx=maxy=-1
                        for yy in range(y0,y1):
                            row=yy*w*n
                            for xx in range(x0,x1):
                                k=row+xx*n; rr,gg,bb=raw[k],raw[k+1],raw[k+2]
                                if max(abs(int(rr)-bx),abs(int(gg)-by),abs(int(bb)-bz))<=10:
                                    minx=min(minx,xx);maxx=max(maxx,xx);miny=min(miny,yy);maxy=max(maxy,yy)
                        if maxx>minx and maxy>miny and maxx-minx>w*.45 and maxy-miny>h*.35:
                            pad=max(3,int(min(w,h)*.012)); minx=max(0,minx-pad);maxx=min(w-1,maxx+pad);miny=max(0,miny-pad);maxy=min(h-1,maxy+pad)
                            sx,sy=r.width/w,r.height/h
                            return {'left':round(max(pr.x0,r.x0+minx*sx),2),'top':round(max(pr.y0,r.y0+miny*sy),2),'right':round(min(pr.x1,r.x0+(maxx+1)*sx),2),'bottom':round(min(pr.y1,r.y0+(maxy+1)*sy),2)}
        except Exception: pass
    # Fallback: render the displayed region and remove obvious outer margins.
    m=max(2,min(8,.012*max(r.width,r.height))); r=fitz.Rect(max(pr.x0,r.x0-m),max(pr.y0,r.y0-m),min(pr.x1,r.x1+m),min(pr.y1,r.y1+m))
    try:
        scale=3.0; pix=page.get_pixmap(matrix=fitz.Matrix(scale,scale),clip=r,alpha=False); w,h,n=pix.width,pix.height,pix.n; raw=pix.samples; ix,iy=int(w*.06),int(h*.06); minx,miny=w,h; maxx=maxy=-1
        for yy in range(iy,max(iy,h-iy)):
            row=yy*w*n
            for xx in range(ix,max(ix,w-ix)):
                k=row+xx*n; rr,gg,bb=raw[k],raw[k+1],raw[k+2]
                if min(rr,gg,bb)<225 or max(rr,gg,bb)-min(rr,gg,bb)>24:minx=min(minx,xx);maxx=max(maxx,xx);miny=min(miny,yy);maxy=max(maxy,yy)
        if maxx>=0:
            pad=max(8,int(min(w,h)*.03)); inv=1/scale; r=fitz.Rect(r.x0+max(ix,minx-pad)*inv,r.y0+max(iy,miny-pad)*inv,r.x0+min(w-ix,maxx+pad+1)*inv,r.y0+min(h-iy,maxy+pad+1)*inv)
    except Exception: pass
    return {'left':round(max(pr.x0,r.x0),2),'top':round(max(pr.y0,r.y0),2),'right':round(min(pr.x1,r.x1),2),'bottom':round(min(pr.y1,r.y1),2)}

def page_question_starts(page):
    out=[]
    for b in page.get_text('blocks'):
        text=str(b[4] or ''); matches=list(QSTART.finditer(text))
        if not matches:continue
        line_h=max(8.0,(float(b[3])-float(b[1]))/max(1,text.count('\n')+1))
        for m in matches:out.append((float(b[1])+text[:m.start()].count('\n')*line_h,int(m.group(1))))
    return sorted(out)
def question_end_pages(qs,subject):
    ends={}
    for i,q in enumerate(qs):
        end=int(q.get('sourcePageEnd') or q['sourcePage'])
        if subject=='Biochemistry':
            nxt=qs[i+1] if i+1<len(qs) else None
            if nxt is None or nxt.get('chapterId')!=q.get('chapterId'):end=int(q['sourcePage'])
        ends[q['id']]=max(int(q['sourcePage']),end)
    return ends
def image_rect_candidates(page):
    out=[];seen=set()
    for im in page.get_images(full=True):
        xref=int(im[0])
        try:rects=page.get_image_rects(xref)
        except Exception:rects=[]
        for r in rects:
            r=fitz.Rect(r); key=(xref,round(r.x0,2),round(r.y0,2),round(r.x1,2),round(r.y1,2))
            if r.get_area()>100 and key not in seen:seen.add(key);out.append((r,xref))
    if out:return out
    for b in page.get_text('dict').get('blocks',[]):
        if b.get('type')==1 and b.get('bbox'):
            r=fitz.Rect(b['bbox'])
            if r.get_area()>100:out.append((r,None))
    return out
def main():
    allmeta={};report={}
    for subject,(pdf_name,data_name) in SUBJECTS.items():
        pdf=ASSETS/pdf_name
        if not pdf.exists():print('missing',pdf,file=sys.stderr);sys.exit(1)
        qs=load_questions(data_name,subject); ends=question_end_pages(qs,subject); starts_by_page={}
        for q in qs:starts_by_page.setdefault(int(q['sourcePage']),{}).setdefault(int(q.get('questionNumber',-1)),[]).append(q)
        active_by_page={}
        for q in qs:
            for pg in range(int(q['sourcePage']),ends[q['id']]+1):active_by_page.setdefault(pg,[]).append(q)
        doc=fitz.open(pdf);assigned={};pages_with_visuals=0;image_blocks=0
        for pno in sorted(active_by_page):
            page=doc[pno-1]; txt=page.get_text('text') or ''
            if SOLUTION.search(txt):continue
            cands=active_by_page[pno]; starts=page_question_starts(page); blocks=image_rect_candidates(page)
            valid=[]
            for r,xref in blocks:
                cy=(r.y0+r.y1)/2; owner=None
                for y,n in starts:
                    if y>cy:break
                    for q in starts_by_page.get(pno,{}).get(n,[]):
                        if q in cands:owner=q
                if owner is None:
                    prev=[q for q in cands if int(q['sourcePage'])<pno]
                    if prev:owner=max(prev,key=lambda q:int(q['sourcePage']))
                if owner is None or not(int(owner['sourcePage'])<=pno<=ends[owner['id']]):continue
                crop=crop_box(page,r,xref)
                if crop:valid.append((owner,r.get_area(),{'type':'source-pdf','source':pdf_name,'page':pno,'crop':crop,'fit':'contain','scale':6.0}))
            if valid:
                pages_with_visuals+=1;image_blocks+=len(valid)
                for owner,area,visual in valid:assigned.setdefault(owner['id'],[]).append((area,visual))
        entries=[];cue_total=0;cue_mapped=0
        for q in qs:
            text=q.get('_display_question',''); cue=bool(VISUAL_CUE.search(text))
            if cue:cue_total+=1
            vals=sorted(assigned.get(q['id'],[]),key=lambda z:z[0],reverse=True)
            if not vals:continue
            if cue:cue_mapped+=1
            visuals=[v for _,v in vals]; entries.append({'match':text,'visual':visuals[0],'visuals':visuals})
        if not entries:print(subject,'NO VALID QUESTION VISUALS',file=sys.stderr);sys.exit(1)
        allmeta[subject]=entries; report[subject]={'questions':len(qs),'mappedQuestions':len(entries),'cueQuestions':cue_total,'cueMapped':cue_mapped,'pagesWithVisuals':pages_with_visuals,'imageBlocksAccepted':image_blocks}; print(subject,'questions',len(qs),'visuals',len(entries),'cue mapped',cue_mapped,'/',cue_total); doc.close()
    for subject,r in report.items():
        if r['mappedQuestions']<10:print('mapping floor failed',subject,r,file=sys.stderr);sys.exit(1)
    OUT.write_text('/* Generated V11 source visual metadata. Exact QBank-indexed PDF image blocks. */\nwindow.SOURCE_VISUALS='+json.dumps(allmeta,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf-8')
    (ASSETS/'source_visual_mapping_report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
if __name__=='__main__':main()
