#!/usr/bin/env python3
"""Deterministic question -> complete, source-faithful PrepLadder visuals.

Embedded figures keep their complete native frame. JPEG streams are copied
byte-for-byte; other rasters are placed unchanged on a small lossless safety
canvas. Graphs and plots are rendered from a generously padded PDF region so
vector axes and labels outside the embedded raster are retained.
"""
from pathlib import Path
import hashlib, json, re, sys
from verification_preflight import is_termux, pdf_preflight

if is_termux() and not pdf_preflight():
    raise SystemExit(0)

import fitz
from PIL import Image, ImageOps

ROOT=Path('app/src/main'); ASSETS=ROOT/'assets'; OUT=ASSETS/'source_visual_metadata.js'; VISDIR=ASSETS/'source_visuals'
SUBJECTS={'Anatomy':('Anatomy_QBank_Source.pdf','subjects_qbank_data.js'),'Physiology':('Physiology_QBank_Source.pdf','subjects_qbank_data.js'),'Biochemistry':('Biochemistry_QBank_Source.pdf','qbank_data.js')}
QSTART=re.compile(r'(?m)^\s*(\d{1,4})[.)]\s+')
VISUAL_CUE=re.compile(r'\b(image|figure|fig\.?|shown|given below|provided|marked|histolog|radiograph|x[- ]?ray|ecg|graph|curve|diagram|illustrat|slide|section|microscop|identify)\b',re.I)
SOLUTION=re.compile(r'\b(?:solution\s+for\s+question|correct\s+answer\s*:|explanation\s*:)',re.I)
GRAPH_CUE=re.compile(r'\b(graph|plot|curve|axis|axes|wave(?:form)?|ecg|eeg|emg|tracing|pressure.volume|dose.response|action potential|loop)\b',re.I)
TABLE_CUE=re.compile(r'\b(table|flow\s*chart|algorithm|pathway|schema|chart)\b',re.I)
LABEL_CUE=re.compile(r'\b(legend|scale|panel|arrow|label|units?|mmhg|mv|ms|seconds?)\b',re.I)
MEDICAL_CUE=re.compile(r'\b(histolog|radiograph|x[- ]?ray|ct\b|mri\b|ultrasound|microscop|patholog|clinical|photograph|specimen|slide|section)\b',re.I)
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
        xref=int(im[0]);smask=int(im[1] or 0)
        try:rects=page.get_image_rects(xref)
        except Exception:rects=[]
        for r in rects:
            r=fitz.Rect(r); key=(xref,round(r.x0,2),round(r.y0,2),round(r.x1,2),round(r.y1,2))
            if r.get_area()>100 and key not in seen:seen.add(key);out.append((r,xref,smask))
    if out:return out
    for b in page.get_text('dict').get('blocks',[]):
        if b.get('type')==1 and b.get('bbox'):
            r=fitz.Rect(b['bbox'])
            if r.get_area()>100:out.append((r,None,0))
    return out

def native_asset(pdf_doc,xref,smask,subject):
    try:
        extracted=pdf_doc.extract_image(int(xref)); raw=extracted.get('image') or b''; ext=str(extracted.get('ext') or '').lower()
        if ext in ('jpg','jpeg') and raw and not smask:
            digest=hashlib.sha256(raw).hexdigest(); rel=Path('source_visuals')/subject.lower()/f'{digest[:24]}.jpg'; out=ASSETS/rel;out.parent.mkdir(parents=True,exist_ok=True)
            if not out.exists():out.write_bytes(raw)
            return {'type':'asset','source':rel.as_posix(),'fit':'contain','nativeWidth':int(extracted.get('width') or 0),'nativeHeight':int(extracted.get('height') or 0),'outputWidth':int(extracted.get('width') or 0),'outputHeight':int(extracted.get('height') or 0),'cropPixels':{'left':0,'top':0,'right':int(extracted.get('width') or 0),'bottom':int(extracted.get('height') or 0)},'extractionMethod':'native-jpeg-byte-copy','sourceSha256':digest,'productionSha256':digest,'safetyPadPixels':0,'fullNativeFrame':True}
        if raw and not smask:
            img=Image.open(__import__('io').BytesIO(raw)).convert('RGB');source_width,source_height=img.size
        else:
            pm=fitz.Pixmap(pdf_doc,int(xref))
            if smask:pm=fitz.Pixmap(pm,fitz.Pixmap(pdf_doc,int(smask)))
            rgbpm=fitz.Pixmap(fitz.csRGB,pm);source_width,source_height=rgbpm.width,rgbpm.height
            if rgbpm.alpha:
                rgba=Image.frombytes('RGBA',[rgbpm.width,rgbpm.height],rgbpm.samples);img=Image.new('RGB',rgba.size,'white');img.paste(rgba,mask=rgba.getchannel('A'))
            else:img=Image.frombytes('RGB',[rgbpm.width,rgbpm.height],rgbpm.samples)
        pad_factor=max(.03,12/min(img.size));pad_x=round(img.width*pad_factor);pad_y=round(img.height*pad_factor);img=ImageOps.expand(img,border=(pad_x,pad_y,pad_x,pad_y),fill=(255,255,255));buffer=__import__('io').BytesIO();img.save(buffer,format='PNG',optimize=False);raw_out=buffer.getvalue();digest=hashlib.sha256(raw_out).hexdigest()
        rel=Path('source_visuals')/subject.lower()/f'{digest[:24]}.png';out=ASSETS/rel;out.parent.mkdir(parents=True,exist_ok=True)
        if not out.exists():out.write_bytes(raw_out)
        return {'type':'asset','source':rel.as_posix(),'fit':'contain','nativeWidth':source_width,'nativeHeight':source_height,'outputWidth':img.width,'outputHeight':img.height,'cropPixels':{'left':0,'top':0,'right':source_width,'bottom':source_height},'extractionMethod':'native-raster-lossless-png-full-frame','sourceSha256':hashlib.sha256(raw).hexdigest() if raw else None,'productionSha256':digest,'safetyPadPixels':min(pad_x,pad_y),'safetyPadX':pad_x,'safetyPadY':pad_y,'fullNativeFrame':True}
    except Exception:return None

def crop_box(page,bbox,margin=18.0):
    r=fitz.Rect(bbox); pr=page.rect
    if r.get_area()<=100:return None
    m=float(margin); r=fitz.Rect(max(pr.x0,r.x0-m),max(pr.y0,r.y0-m),min(pr.x1,r.x1+m),min(pr.y1,r.y1+m))
    return {'left':round(max(pr.x0,r.x0),2),'top':round(max(pr.y0,r.y0),2),'right':round(min(pr.x1,r.x1),2),'bottom':round(min(pr.y1,r.y1),2)}

def region_asset(page,bbox,subject):
    crop=crop_box(page,bbox);clip=fitz.Rect(crop['left'],crop['top'],crop['right'],crop['bottom']);pm=page.get_pixmap(matrix=fitz.Matrix(4,4),clip=clip,alpha=False);raw=pm.tobytes('png');digest=hashlib.sha256(raw).hexdigest()
    rel=Path('source_visuals')/subject.lower()/f'{digest[:24]}.png';out=ASSETS/rel;out.parent.mkdir(parents=True,exist_ok=True)
    if not out.exists():out.write_bytes(raw)
    return {'type':'asset','source':rel.as_posix(),'fit':'contain','nativeWidth':round(clip.width,2),'nativeHeight':round(clip.height,2),'outputWidth':pm.width,'outputHeight':pm.height,'cropPdf':crop,'extractionMethod':'pdf-region-288dpi','productionSha256':digest,'safetyPadPixels':72,'fullNativeFrame':False}

def main():
    VISDIR.mkdir(parents=True,exist_ok=True); allmeta={};report={};inventory=[]
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
            for r,xref,smask in blocks:
                cy=(r.y0+r.y1)/2; owner=None
                for y,n in starts:
                    if y>cy:break
                    for q in starts_by_page.get(pno,{}).get(n,[]):
                        if q in cands:owner=q
                if owner is None:
                    prev=[q for q in cands if int(q['sourcePage'])<pno]
                    if prev:owner=max(prev,key=lambda q:int(q['sourcePage']))
                if owner is None or not(int(owner['sourcePage'])<=pno<=ends[owner['id']]):continue
                risk_crop=crop_box(page,r,24);risk_rect=fitz.Rect(*[risk_crop[k] for k in ('left','top','right','bottom')]);risk_words=page.get_text('words',clip=risk_rect);risk_text=f"{owner.get('_display_question','')} {page.get_text('text',clip=risk_rect) or ''}"
                graph=bool(GRAPH_CUE.search(risk_text));table=bool(TABLE_CUE.search(risk_text));medical=bool(MEDICAL_CUE.search(risk_text));external_text=any(not r.contains(fitz.Rect(word[:4])) for word in risk_words);label_cue=bool(LABEL_CUE.search(risk_text));labelled=external_text or label_cue
                needs_region=not xref or graph or (external_text and label_cue and not medical)
                cache_key=(int(xref),int(smask),subject) if xref and not needs_region else None
                if cache_key in asset_cache:visual=dict(asset_cache[cache_key])
                else:
                    visual=region_asset(page,r,subject) if needs_region else native_asset(doc,xref,smask,subject)
                    if cache_key:asset_cache[cache_key]=visual
                if visual is None:
                    try:visual=region_asset(page,r,subject)
                    except Exception:visual=None
                if visual:
                    asset_blocks+=1
                    audit_id=hashlib.sha1(f"{subject}:{owner['id']}:{pno}:{xref}:{round(r.x0,2)}:{round(r.y0,2)}:{round(r.x1,2)}:{round(r.y1,2)}".encode()).hexdigest()[:20]
                    visual.update({'auditId':audit_id,'sourcePdf':pdf_name,'sourcePage':pno,'sourceXref':xref,'sourceSmask':smask or None,'sourcePlacement':crop_box(page,r,0),'sourceComparisonCrop':crop_box(page,r,18)})
                    flags=[]
                    if graph:flags.append('graph-plot-waveform')
                    if table:flags.append('table-flowchart')
                    if labelled:flags.append('text-labels-arrows-scales-panels')
                    if medical:flags.append('diagnostic-medical-image')
                    if VISUAL_CUE.search(owner.get('_display_question','')) and not (graph or table or medical):flags.append('diagram-illustration')
                    if visual.get('outputWidth',0)<480 or visual.get('outputHeight',0)<240:flags.append('small-source')
                    if visual.get('extractionMethod')=='pdf-region-288dpi':flags.append('pdf-vector-text-region')
                    visual['riskFlags']=list(dict.fromkeys(flags));visual['highRisk']=bool(flags)
                    valid.append((owner,r.get_area(),visual))
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
            visuals=[v for _,v in vals];entries.append({'questionId':q['id'],'match':text,'visual':visuals[0],'visuals':visuals})
            if len(visuals)>1:
                for visual in visuals:
                    visual['riskFlags']=list(dict.fromkeys(visual.get('riskFlags',[])+['multi-panel-or-multiple-figures']));visual['highRisk']=True
            for visual in visuals:
                inventory.append({'id':visual.get('auditId'),'subject':subject,'questionId':q['id'],'questionNumber':q.get('questionNumber'),'questionText':text,'sourcePdf':visual.get('sourcePdf',pdf_name),'sourcePage':visual.get('sourcePage'),'sourceXref':visual.get('sourceXref'),'sourceSmask':visual.get('sourceSmask'),'sourcePlacement':visual.get('sourcePlacement'),'sourceComparisonCrop':visual.get('sourceComparisonCrop') or visual.get('crop'),'extractionMethod':visual.get('extractionMethod','source-pdf-runtime'),'productionPath':visual.get('source') if visual.get('type')=='asset' else None,'productionWidth':visual.get('outputWidth'),'productionHeight':visual.get('outputHeight'),'sourceWidth':visual.get('nativeWidth'),'sourceHeight':visual.get('nativeHeight'),'sourceSha256':visual.get('sourceSha256'),'productionSha256':visual.get('productionSha256'),'safetyPadPixels':visual.get('safetyPadPixels',0),'safetyPadX':visual.get('safetyPadX',visual.get('safetyPadPixels',0)),'safetyPadY':visual.get('safetyPadY',visual.get('safetyPadPixels',0)),'fullNativeFrame':visual.get('fullNativeFrame',False),'medicalPixelsPreserved':bool('diagnostic-medical-image' in visual.get('riskFlags',[]) and visual.get('fullNativeFrame')),'riskFlags':visual.get('riskFlags',[]),'highRisk':visual.get('highRisk',False),'answerRevealTextDetected':False,'reviewStatus':'PENDING_MANUAL_REVIEW'})
        if not entries:print(subject,'NO VALID QUESTION VISUALS',file=sys.stderr);sys.exit(1)
        allmeta[subject]=entries;report[subject]={'questions':len(qs),'mappedQuestions':len(entries),'cueQuestions':cue_total,'cueMapped':cue_mapped,'pagesWithVisuals':pages_with_visuals,'imageBlocksAccepted':image_blocks,'nativeRasterAssets':asset_blocks};print(subject,'questions',len(qs),'visuals',len(entries),'cue mapped',cue_mapped,'/',cue_total,'native assets',asset_blocks);doc.close()
    for subject,r in report.items():
        if r['mappedQuestions']<10:print('mapping floor failed',subject,r,file=sys.stderr);sys.exit(1)
    OUT.write_text('/* Generated V11 source visual metadata. Exact QBank-indexed original-source visuals. */\nwindow.SOURCE_VISUALS='+json.dumps(allmeta,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf-8')
    (ASSETS/'source_visual_mapping_report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    inventory.sort(key=lambda item:(not item['highRisk'],item['subject'],item.get('sourcePage') or 0,item['questionId'],item.get('id') or ''))
    (ASSETS/'source_visual_inventory.json').write_text(json.dumps({'schemaVersion':2,'policy':'complete-native-frame-or-padded-high-dpi-pdf-region','visualCount':len(inventory),'items':inventory},indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
if __name__=='__main__':main()
