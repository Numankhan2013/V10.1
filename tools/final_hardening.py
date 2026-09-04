from pathlib import Path
import json
import re
import fitz

HTML = Path('app/src/main/assets/index.html')
DATA = Path('app/src/main/assets/subjects_qbank_data.js')
MAP = Path('app/src/main/assets/subject_source_solution_maps.js')


def question_ids(raw, subject):
    pat = re.compile(r'["\'](?:id|questionId)["\']\s*:\s*["\'](' + re.escape(subject) + r'-\d+-\d+)["\']')
    ids = pat.findall(raw)
    # Preserve order while removing accidental duplicate occurrences.
    out=[]; seen=set()
    for qid in ids:
        if qid not in seen:
            seen.add(qid); out.append(qid)
    return out


def build_map(pdf_path, ids, subject):
    doc = fitz.open(pdf_path)
    markers=[]
    for page_no, page in enumerate(doc, 1):
        for block in page.get_text('blocks'):
            text=block[4]
            for m in re.finditer(r'Solution\s+for\s+Question\s+(\d+)\s*:', text, re.I):
                markers.append((page_no, float(block[1]), int(m.group(1))))
    doc.close()
    if len(markers) != len(ids):
        raise SystemExit(f'{subject}: expected {len(ids)} solution markers, found {len(markers)}')
    items=[]
    for i,qid in enumerate(ids):
        p,y,_=markers[i]
        nxt=markers[i+1] if i+1<len(markers) else None
        if nxt is None:
            seg=[{'page':p,'top':round(y,2)}]
        else:
            np,ny,_=nxt
            if np==p:
                seg=[{'page':p,'top':round(y,2),'bottom':round(ny,2)}]
            else:
                seg=[{'page':p,'top':round(y,2)}]
                for mid in range(p+1,np): seg.append({'page':mid})
                seg.append({'page':np,'bottom':round(ny,2)})
        items.append({'id':qid,'segments':seg})
    return items

raw=DATA.read_text(encoding='utf-8')
result={}
for subject,pdf in [
    ('physiology', Path('app/src/main/assets/Physiology_QBank_Source.pdf')),
    ('anatomy', Path('app/src/main/assets/Anatomy_QBank_Source.pdf')),
]:
    if not pdf.exists():
        print(f'{subject}: source PDF absent; leaving that map empty')
        result[subject]=[]
        continue
    ids=question_ids(raw, subject)
    if not ids:
        raise SystemExit(f'{subject}: could not extract question IDs from subjects_qbank_data.js')
    result[subject]=build_map(pdf, ids, subject)
    print(f'{subject}: generated {len(result[subject])} exact solution mappings')

MAP.write_text('window.SUBJECT_SOURCE_SOLUTIONS='+json.dumps(result,separators=(',',':'))+';\n', encoding='utf-8')

s=HTML.read_text(encoding='utf-8')
map_tag='<script src="subject_source_solution_maps.js"></script>'
if map_tag not in s:
    s=s.replace('</head>',map_tag+'\n</head>',1)

# Replace the lexical renderer installed by repair_source_solution_renderer.py.
start=s.find('function renderExplanationText(text,question){')
if start<0: raise SystemExit('renderExplanationText not found')
brace=s.find('{',start); depth=0; end=-1
for i in range(brace,len(s)):
    if s[i]=='{': depth+=1
    elif s[i]=='}':
        depth-=1
        if depth==0: end=i+1; break
if end<0: raise SystemExit('renderExplanationText end not found')
replacement=r'''function renderExplanationText(text,question){
    const id=String(question?.id||'').toLowerCase();
    const subject=id.startsWith('anatomy-')?'anatomy':window.sourceSubjectV14(question);
    const label=subject==='physiology'?'Physiology':(subject==='anatomy'?'Anatomy':'Biochemistry');
    let segments=[];
    if(subject==='biochemistry' && window.BIOCHEM_SOURCE_SOLUTIONS){
      const hit=window.BIOCHEM_SOURCE_SOLUTIONS.find(x=>x.id===String(question?.id||''));
      segments=hit?.segments||[];
    } else if(window.SUBJECT_SOURCE_SOLUTIONS?.[subject]) {
      const hit=window.SUBJECT_SOURCE_SOLUTIONS[subject].find(x=>x.id===String(question?.id||''));
      segments=hit?.segments||[];
    }
    if(!segments.length){
      const ref=String(question?.sourceRef||'');
      const m=ref.match(/Solution\s+Pages?\s+(\d+)(?:\s*-\s*(\d+))?/i);
      if(m){const a=Number(m[1]),b=Number(m[2]||m[1]);for(let p=a;p<=b;p++)segments.push({page:p});}
    }
    if(!segments.length)return '';
    const url=seg=>`https://qbank.local/${subject}/pdf?page=${encodeURIComponent(seg.page)}&scale=3.5${seg.top!=null?`&top=${encodeURIComponent(seg.top)}`:''}${seg.bottom!=null?`&bottom=${encodeURIComponent(seg.bottom)}`:''}`;
    return `<div class="source-pdf-explanation"><div class="source-pdf-scroll"><div class="source-pdf-head">Original source solution · ${label}</div>${segments.map(seg=>`<div class="source-pdf-page" onclick="window.openSourceZoom(this.querySelector('img'))"><img loading="lazy" src="${url(seg)}" data-source-page="${seg.page}" alt="Original ${label} PDF solution page ${seg.page}"></div>`).join('')}<div class="source-pdf-note">Original PDF rendering only. No explanation text is parsed or reconstructed.</div></div></div>`;
  }'''
s=s[:start]+replacement+s[end:]

# Make the Test Analysis CTA direct and deterministic.
s=s.replace('data-v102-review-cta="1" data-review-test-id="${esc(t.id)}">Review Solutions</button>', 'data-review-test-id="${esc(t.id)}" onclick="window.QB.reviewTest(this.getAttribute(\'data-review-test-id\'))">Review Solutions</button>')
s=s.replace('data-v102-review-cta="1" data-review-test-id="${esc(t.id)}"', 'data-review-test-id="${esc(t.id)}" onclick="window.QB.reviewTest(this.getAttribute(\'data-review-test-id\'))"')

# The submit notification must not survive navigation to Test Analysis.
s=s.replace("state.activeSession=null;saveState();navigate('result',test.id);showToast(auto?'Time expired — test submitted automatically.':'Test submitted.','good');", "state.activeSession=null;saveState();document.querySelectorAll('#toast-root .toast').forEach(e=>e.remove());navigate('result',test.id);")

# Install a final, direct review implementation after all older review wrappers.
final_review=r'''<script id="final-cbt-review-fix">
(function(){
  function openReview(testId){
    try{
      const qb=window.QB;if(!qb||typeof qb.getState!=='function')return false;
      const st=qb.getState();const wanted=decodeURIComponent(String(testId||''));
      const t=(Array.isArray(st.tests)?st.tests:[]).find(x=>String(x.id)===wanted||String(x.id)===String(testId));
      if(!t||!Array.isArray(t.questionIds)||!t.questionIds.length)return false;
      st.activeSession={id:'review_'+String(t.id),mode:'review',sourceTestId:String(t.id),title:'Review · '+String(t.title||'Completed Test'),questionIds:t.questionIds.slice(),index:0,answers:Object.assign({},t.answers||{}),submitted:t.questionIds.reduce(function(a,id){a[id]=Object.prototype.hasOwnProperty.call(t.answers||{},id);return a;},{}),startedAt:t.createdAt||Date.now(),questionTimes:Object.assign({},t.questionTimes||{})};
      localStorage.setItem('qbank_state_v1',JSON.stringify(st));
      location.hash='#review-test/'+encodeURIComponent(String(t.id));
      return true;
    }catch(e){console.error('Final Review Solutions fix failed',e);return false;}
  }
  window.QB=window.QB||{};window.QB.reviewTest=openReview;
})();
</script>'''
s=s.replace('</body>',final_review+'\n</body>',1)

# Replace the weak V14 zoom with true touch pinch/pan and bounded zoom.
zoom_css=r'''<style id="final-source-zoom-css">
.source-pdf-zoom{position:fixed;inset:0;z-index:10000;background:rgba(8,9,17,.97);display:flex;flex-direction:column}.source-pdf-zoombar{height:58px;display:flex;align-items:center;justify-content:space-between;padding:7px 10px;color:#fff;flex:none}.source-pdf-zoomtitle{font-size:12px;font-weight:800;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.source-pdf-zoombar button{min-width:38px;height:38px;margin-left:5px;border:1px solid rgba(255,255,255,.25);border-radius:10px;background:rgba(255,255,255,.1);color:#fff;font-size:19px}.source-pdf-zoomstage{position:relative;flex:1;overflow:hidden;touch-action:none;display:block}.source-pdf-zoomimg{position:absolute;left:0;top:0;max-width:none;max-height:none;width:auto;height:auto;transform-origin:0 0;user-select:none;-webkit-user-drag:none;will-change:transform}
</style>'''
zoom_js=r'''<script id="final-source-zoom-js">
(function(){
  function openSourceZoom(img){
    document.getElementById('source-pdf-zoom')?.remove();
    const b=document.createElement('div');b.id='source-pdf-zoom';b.className='source-pdf-zoom';
    b.innerHTML=`<div class="source-pdf-zoombar"><div class="source-pdf-zoomtitle">Original source · PDF page ${String(img.dataset.sourcePage||'')}</div><div><button id="spz-minus">−</button><button id="spz-reset">Fit</button><button id="spz-plus">+</button><button id="spz-close">×</button></div></div><div class="source-pdf-zoomstage"><img class="source-pdf-zoomimg" src="${img.src}" alt="Original source"></div>`;
    document.body.appendChild(b);
    const st=b.querySelector('.source-pdf-zoomstage'),i=b.querySelector('.source-pdf-zoomimg');
    let scale=1,x=0,y=0,baseScale=1,dragStart=null,pointers=new Map(),pinchDist=0,pinchScale=1,pinchMid=null;
    const clamp=()=>{const maxX=Math.max(0,(i.naturalWidth*scale-st.clientWidth)/2+st.clientWidth*.45),maxY=Math.max(0,(i.naturalHeight*scale-st.clientHeight)/2+st.clientHeight*.45);x=Math.max(-maxX,Math.min(maxX,x));y=Math.max(-maxY,Math.min(maxY,y));};
    const apply=()=>{clamp();i.style.transform=`translate3d(${x}px,${y}px,0) scale(${scale})`;};
    const fit=()=>{if(!i.naturalWidth)return;baseScale=Math.min(st.clientWidth/i.naturalWidth,st.clientHeight/i.naturalHeight);scale=Math.max(.25,Math.min(1,baseScale));x=(st.clientWidth-i.naturalWidth*scale)/2;y=(st.clientHeight-i.naturalHeight*scale)/2;apply();};
    const zoomAt=(next,cx=st.clientWidth/2,cy=st.clientHeight/2)=>{const old=scale;next=Math.max(baseScale*.75,Math.min(6,next));const ix=(cx-x)/old,iy=(cy-y)/old;scale=next;x=cx-ix*scale;y=cy-iy*scale;apply();};
    i.addEventListener('load',fit);if(i.complete)fit();
    b.querySelector('#spz-close').onclick=()=>b.remove();b.querySelector('#spz-reset').onclick=fit;b.querySelector('#spz-plus').onclick=()=>zoomAt(scale*1.35);b.querySelector('#spz-minus').onclick=()=>zoomAt(scale/1.35);
    st.addEventListener('pointerdown',e=>{e.preventDefault();st.setPointerCapture?.(e.pointerId);pointers.set(e.pointerId,{x:e.clientX,y:e.clientY});if(pointers.size===1){dragStart={x:e.clientX,y:e.clientY,ox:x,oy:y};}else if(pointers.size===2){const a=[...pointers.values()];pinchDist=Math.hypot(a[0].x-a[1].x,a[0].y-a[1].y);pinchScale=scale;pinchMid={x:(a[0].x+a[1].x)/2,y:(a[0].y+a[1].y)/2};}});
    st.addEventListener('pointermove',e=>{if(!pointers.has(e.pointerId))return;e.preventDefault();pointers.set(e.pointerId,{x:e.clientX,y:e.clientY});const a=[...pointers.values()];if(a.length===1&&dragStart){x=dragStart.ox+e.clientX-dragStart.x;y=dragStart.oy+e.clientY-dragStart.y;apply();}else if(a.length===2&&pinchDist){const d=Math.hypot(a[0].x-a[1].x,a[0].y-a[1].y);zoomAt(pinchScale*d/pinchDist,pinchMid.x,pinchMid.y);}});
    const end=e=>{pointers.delete(e.pointerId);if(pointers.size<2)pinchDist=0;if(pointers.size===0)dragStart=null;};['pointerup','pointercancel','pointerleave'].forEach(ev=>st.addEventListener(ev,end));
    st.addEventListener('dblclick',e=>{e.preventDefault();zoomAt(scale<baseScale*2?scale*2:baseScale,e.clientX,e.clientY);});
    b.addEventListener('click',e=>{if(e.target===b)b.remove();});
  }
  window.openSourceZoom=openSourceZoom;
})();
</script>'''
s=s.replace('</body>',zoom_css+'\n'+zoom_js+'\n</body>',1)
HTML.write_text(s,encoding='utf-8')
print('Final hardening applied: exact Physiology/Anatomy solution crops, touch pinch/pan zoom, deterministic CBT review, and submit-toast cleanup.')
