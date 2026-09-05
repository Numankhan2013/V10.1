#!/usr/bin/env python3
"""Deterministic question -> original source-PDF visual assets.

The PDF remains the source of truth. For embedded raster figures we extract the
native image losslessly to PNG and crop only the surrounding presentation
canvas/frame so the question shows the actual figure at the highest source
quality available. PDF-region rendering remains the fallback for figures that
are not embedded rasters.
"""
from pathlib import Path
import hashlib, json, re, sys
import fitz
from PIL import Image, ImageChops, ImageStat

ROOT=Path('app/src/main'); ASSETS=ROOT/'assets'; OUT=ASSETS/'source_visual_metadata.js'; VISDIR=ASSETS/'source_visuals'
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

def crop_native_figure(pm):
    """Tight-crop meaningful figure content while removing presentation canvas/frame."""
    if pm.width < 40 or pm.height < 40:return None
    img=Image.frombytes('RGB',[pm.width,pm.height],pm.samples)
    w,h=img.size; colors=[]
    for fx,fy in ((.08,.08),(.50,.08),(.92,.08),(.08,.50),(.50,.50),(.92,.50),(.08,.92),(.50,.92),(.92,.92)):
        cx,cy=int(w*fx),int(h*fy); rw=max(3,int(w*.02)); rh=max(3,int(h*.02))
        patch=img.crop((max(0,cx-rw),max(0,cy-rh),min(w,cx+rw),min(h,cy+rh)))
        rgb=tuple(int(round(v)) for v in ImageStat.Stat(patch).mean[:3])
        if min(rgb)>=220 and max(rgb)-min(rgb)<=40:colors.append(rgb)
    if not colors:colors=[(248,248,248)]
    bgs=[]
    for c in colors:
        if all(max(abs(c[i]-b[i]) for i in range(3))>8 for b in bgs):bgs.append(c)
        if len(bgs)>=3:break
    masks=[]
    for bg in bgs:
        diff=ImageChops.difference(img,Image.new('RGB',(w,h),bg)).convert('L')
        masks.append(diff.point(lambda p:255 if p>12 else 0))
    mask=masks[0]
    for other in masks[1:]:mask=ImageChops.lighter(mask,other)
    margin=int(min(w,h)*.08)
    mask.paste(0,(0,0,w,margin));mask.paste(0,(0,h-margin,w,h));mask.paste(0,(0,0,margin,h));mask.paste(0,(w-margin,0,w,h))
    bbox=mask.getbbox()
    if not bbox:return None
    minx,miny,maxx,maxy=bbox
    if (maxx-minx)<w*.20 or (maxy-miny)<h*.12:return None
    pad=max(4,int(min(w,h)*.018))
    box=(max(0,minx-pad),max(0,miny-pad),min(w,maxx+pad),min(h,maxy+pad))
    return img.crop(box),box

def native_asset(pdf_doc,xref,subject):
    try:
        pm=fitz.Pixmap(pdf_doc,int(xref)); result=crop_native_figure(pm)
        if not result:return None
        img,box=result; digest=hashlib.sha1(f'{subject}:{xref}:{box}'.encode()).hexdigest()[:16]
        rel=Path('source_visuals')/subject.lower()/f'{digest}.png'; out=ASSETS/rel; out.parent.mkdir(parents=True,exist_ok=True)
        if not out.exists():img.save(out,format='PNG',optimize=False)
        return {'type':'asset','source':rel.as_posix(),'fit':'contain','nativeWidth':pm.width,'nativeHeight':pm.height,'cropPixels':{'left':box[0],'top':box[1],'right':box[2],'bottom':box[3]}}
    except Exception:return None

def crop_box(page,bbox):
    r=fitz.Rect(bbox); pr=page.rect
    if r.get_area()<=100:return None
    m=max(2,min(8,.012*max(r.width,r.height))); r=fitz.Rect(max(pr.x0,r.x0-m),max(pr.y0,r.y0-m),min(pr.x1,r.x1+m),min(pr.y1,r.y1+m))
    return {'left':round(max(pr.x0,r.x0),2),'top':round(max(pr.y0,r.y0),2),'right':round(min(pr.x1,r.x1),2),'bottom':round(min(pr.y1,r.y1),2)}

def main():
    VISDIR.mkdir(parents=True,exist_ok=True); allmeta={};report={}
    for subject,(pdf_name,data_name) in SUBJECTS.items():
        pdf=ASSETS/pdf_name
        if not pdf.exists():print('missing',pdf,file=sys.stderr);sys.exit(1)
        qs=load_questions(data_name,subject); ends=question_end_pages(qs,subject); starts_by_page={}
        for q in qs:starts_by_page.setdefault(int(q['sourcePage']),{}).setdefault(int(q.get('questionNumber',-1)),[]).append(q)
        active_by_page={}
        for q in qs:
            for pg in range(int(q['sourcePage']),ends[q['id']]+1):active_by_page.setdefault(pg,[]).append(q)
        doc=fitz.open(pdf);assigned={};pages_with_visuals=0;image_blocks=0;asset_blocks=0;asset_cache={}
        for pno in sorted(active_by_page):
            page=doc[pno-1]; txt=page.get_text('text') or ''
            if SOLUTION.search(txt):continue
            cands=active_by_page[pno]; starts=page_question_starts(page); blocks=image_rect_candidates(page); valid=[]
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
                cache_key=(int(xref),subject) if xref else None
                if cache_key in asset_cache:visual=asset_cache[cache_key]
                else:
                    visual=native_asset(doc,xref,subject) if xref else None
                    if cache_key:asset_cache[cache_key]=visual
                if visual:asset_blocks+=1;valid.append((owner,r.get_area(),visual))
                else:
                    crop=crop_box(page,r)
                    if crop:valid.append((owner,r.get_area(),{'type':'source-pdf','source':pdf_name,'page':pno,'crop':crop,'fit':'contain','scale':8.0}))
            if valid:
                pages_with_visuals+=1;image_blocks+=len(valid)
                for owner,area,visual in valid:assigned.setdefault(owner['id'],[]).append((area,visual))
        entries=[];cue_total=0;cue_mapped=0
        for q in qs:
            text=q.get('_display_question','');cue=bool(VISUAL_CUE.search(text))
            if cue:cue_total+=1
            vals=sorted(assigned.get(q['id'],[]),key=lambda z:z[0],reverse=True)
            if not vals:continue
            if cue:cue_mapped+=1
            visuals=[v for _,v in vals];entries.append({'match':text,'visual':visuals[0],'visuals':visuals})
        if not entries:print(subject,'NO VALID QUESTION VISUALS',file=sys.stderr);sys.exit(1)
        allmeta[subject]=entries;report[subject]={'questions':len(qs),'mappedQuestions':len(entries),'cueQuestions':cue_total,'cueMapped':cue_mapped,'pagesWithVisuals':pages_with_visuals,'imageBlocksAccepted':image_blocks,'nativeRasterAssets':asset_blocks};print(subject,'questions',len(qs),'visuals',len(entries),'cue mapped',cue_mapped,'/',cue_total,'native assets',asset_blocks);doc.close()
    for subject,r in report.items():
        if r['mappedQuestions']<10:print('mapping floor failed',subject,r,file=sys.stderr);sys.exit(1)
    OUT.write_text('/* Generated V11 source visual metadata. Exact QBank-indexed original-source visuals. */\nwindow.SOURCE_VISUALS='+json.dumps(allmeta,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf-8')
    (ASSETS/'source_visual_mapping_report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
if __name__=='__main__':main()
