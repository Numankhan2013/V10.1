from pathlib import Path
import re

p = Path('app/src/main/assets/index.html')
s = p.read_text()
marker = '<!-- V103_REVIEW_EXPLANATION_OVERLAY -->'

css = r'''
<style id="v103-review-explanation-css">
.review-mode .question-card,.review-question .question-card{border-color:#dfe2ec}
.review-mode .option.correct,.review-question .option.correct{box-shadow:0 0 0 1px rgba(21,154,116,.06)}
.review-mode .option.wrong,.review-question .option.wrong{box-shadow:0 0 0 1px rgba(223,78,82,.06)}
.explanation-rich{display:grid;gap:11px;margin-top:15px}
.explanation-rich .ex-section{padding:13px 14px;border:1px solid var(--line);border-radius:13px;background:#fff}
.explanation-rich .ex-heading{font-weight:800;font-size:13px;margin-bottom:7px;color:var(--primary)}
.explanation-rich .ex-p{font-size:13px;line-height:1.62;color:#3e4050;margin:0;white-space:pre-wrap}
.explanation-rich ul,.explanation-rich ol{margin:5px 0 0 20px;padding:0;color:#3e4050;font-size:13px;line-height:1.6}
.explanation-rich li{padding-left:3px;margin:3px 0}
</style>
'''

js = r'''
<script id="v103-review-explanation-js">
(function(){
  'use strict';
  const STORAGE_KEY='qbank_state_v1';
  function esc(v){return String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));}
  function richExplanation(text){
    const raw=String(text??'').replace(/\r\n?/g,'\n').trim();
    if(!raw) return '';
    const lines=raw.split('\n'), blocks=[]; let para=[]; let listType=null, items=[];
    const flushPara=()=>{if(para.length){blocks.push('<p class="ex-p">'+esc(para.join(' ').replace(/\s+/g,' ').trim())+'</p>');para=[];}};
    const flushList=()=>{if(!items.length)return;blocks.push('<'+listType+'>'+items.map(x=>'<li>'+esc(x)+'</li>').join('')+'</'+listType+'>');items=[];listType=null;};
    for(const line0 of lines){
      const line=line0.trim();
      if(!line){flushPara();flushList();continue;}
      const heading=line.match(/^(?:[A-Z][A-Za-z0-9 /&()'’:-]{2,80})\s*:\s*$/);
      if(heading){flushPara();flushList();blocks.push('<div class="ex-heading">'+esc(line.slice(0,-1))+'</div>');continue;}
      const m=line.match(/^(?:[-•▪◦*]|\d+[.)])\s+(.*)$/);
      if(m){flushPara();const ordered=/^\d/.test(line);const type=ordered?'ol':'ul';if(listType&&listType!==type)flushList();listType=type;items.push(m[1]);continue;}
      flushList();para.push(line);
    }
    flushPara();flushList();
    return '<div class="explanation-rich">'+blocks.join('')+'</div>';
  }
  window.QB_V103_EXPLANATION=richExplanation;

  function persist(state){try{localStorage.setItem(STORAGE_KEY,JSON.stringify(state));}catch(e){console.error('V103 review persistence failed',e);}}
  function reviewSessionFromTest(t){
    const answers=Object.assign({},t.answers||{});
    return {id:'review_'+String(t.id),mode:'review',sourceTestId:String(t.id),title:'Review · '+String(t.title||'Completed Test'),questionIds:Array.isArray(t.questionIds)?t.questionIds.slice():[],index:0,answers:answers,submitted:Object.fromEntries((t.questionIds||[]).map(id=>[id,Object.prototype.hasOwnProperty.call(answers,id)])),startedAt:t.createdAt||Date.now(),questionTimes:Object.assign({},t.questionTimes||{})};
  }
  function installReview(){
    if(!window.QB || typeof window.QB.reviewTest!=='function' || typeof window.QB.getState!=='function') return false;
    const originalReview=window.QB.reviewTest;
    if(originalReview.__v103Wrapped) return true;
    function reviewTest(testId){
      try{
        const state=window.QB.getState();
        const wanted=decodeURIComponent(String(testId??''));
        const t=(Array.isArray(state.tests)?state.tests:[]).find(x=>String(x.id)===wanted);
        if(!t || !Array.isArray(t.questionIds) || !t.questionIds.length){console.warn('V103 review: completed test not found',wanted);return false;}
        state.activeSession=reviewSessionFromTest(t);
        persist(state);
        location.hash='#review-test/'+encodeURIComponent(String(t.id));
      }catch(e){console.error('V103 review navigation failed',e);}
      return false;
    }
    reviewTest.__v103Wrapped=true;
    window.QB.reviewTest=reviewTest;

    const originalNext=window.QB.nextQ;
    if(typeof originalNext==='function'&&!originalNext.__v103Wrapped){
      function nextQ(){
        const state=window.QB.getState(); const s=state&&state.activeSession;
        if(s&&s.mode==='review'){
          if(s.index<s.questionIds.length-1){s.index++;persist(state);location.hash='#review-test/'+encodeURIComponent(String(s.sourceTestId));}
          return false;
        }
        return originalNext.apply(this,arguments);
      }
      nextQ.__v103Wrapped=true; window.QB.nextQ=nextQ;
    }
    const originalPrev=window.QB.prevQ;
    if(typeof originalPrev==='function'&&!originalPrev.__v103Wrapped){
      function prevQ(){
        const state=window.QB.getState(); const s=state&&state.activeSession;
        if(s&&s.mode==='review'){
          if(s.index>0){s.index--;persist(state);location.hash='#review-test/'+encodeURIComponent(String(s.sourceTestId));}
          return false;
        }
        return originalPrev.apply(this,arguments);
      }
      prevQ.__v103Wrapped=true; window.QB.prevQ=prevQ;
    }
    return true;
  }
  const timer=setInterval(()=>{if(installReview())clearInterval(timer);},50); setTimeout(()=>clearInterval(timer),5000);
  function format(){
    document.querySelectorAll('.feedback-body,.explanation,.explanation-body').forEach(el=>{
      if(el.dataset.v103Formatted==='1')return;
      const txt=el.textContent||'';if(!txt.trim())return;
      const rich=richExplanation(txt);if(rich){el.innerHTML=rich;el.dataset.v103Formatted='1';}
    });
  }
  new MutationObserver(format).observe(document.documentElement,{childList:true,subtree:true});
  format();
})();
</script>
'''

block = css + js + '\n' + marker
pattern = r'<style id="v103-review-explanation-css">.*?</script>\s*<!-- V103_REVIEW_EXPLANATION_OVERLAY -->'
if marker in s:
    s = re.sub(pattern, lambda m: block, s, count=1, flags=re.S)
else:
    s = s.replace('</head>', css + '</head>', 1)
    s = s.replace('</body>', js + '\n' + marker + '\n</body>', 1)
p.write_text(s)
print('V10.3 overlay updated')
