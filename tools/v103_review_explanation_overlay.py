from pathlib import Path

p = Path('app/src/main/assets/index.html')
s = p.read_text()
marker = '<!-- V103_REVIEW_EXPLANATION_OVERLAY -->'
if marker in s:
    print('overlay already present')
    raise SystemExit

css = r'''
<style id="v103-review-explanation-css">
.review-mode .question-card,.review-question .question-card{border-color:#dfe2ec}
.review-mode .option.correct,.review-question .option.correct{box-shadow:0 0 0 1px rgba(21,154,116,.06)}
.review-mode .option.wrong,.review-question .option.wrong{box-shadow:0 0 0 1px rgba(223,78,82,.06)}
.explanation-rich{display:grid;gap:11px;margin-top:15px}
.explanation-rich .ex-section{padding:13px 14px;border:1px solid var(--line);border-radius:13px;background:#fff}
.explanation-rich .ex-heading{font-weight:800;font-size:13px;margin-bottom:7px;color:var(--primary)}
.explanation-rich .ex-p{font-size:13px;line-height:1.62;color:#3e4050;margin:0 0 7px;white-space:pre-wrap}
.explanation-rich .ex-p:last-child{margin-bottom:0}
.explanation-rich ul,.explanation-rich ol{margin:5px 0 0 20px;padding:0;color:#3e4050;font-size:13px;line-height:1.6}
.explanation-rich li{padding-left:3px;margin:3px 0}
.explanation-rich .ex-key{font-weight:800;color:var(--ink)}
</style>
'''

js = r'''
<script id="v103-review-explanation-js">
(function(){
  'use strict';
  function esc(v){return String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));}
  function richExplanation(text){
    const raw=String(text??'').replace(/\r\n?/g,'\n').trim();
    if(!raw) return '';
    const lines=raw.split('\n'), blocks=[]; let para=[];
    const flush=()=>{if(para.length){blocks.push('<p class="ex-p">'+esc(para.join(' ').replace(/\s+/g,' ').trim())+'</p>');para=[];}};
    for(const line0 of lines){
      const line=line0.trim();
      if(!line){flush();continue;}
      if(/^(?:[A-Z][A-Za-z0-9 /&()'’:-]{2,80})\s*:$/.test(line)){flush();blocks.push('<div class="ex-heading">'+esc(line.slice(0,-1))+'</div>');continue;}
      const m=line.match(/^(?:[-•▪◦*]|\d+[.)])\s+(.*)$/);
      if(m){flush();const ordered=/^\d/.test(line);blocks.push(ordered?'<ol><li>'+esc(m[1])+'</li></ol>':'<ul><li>'+esc(m[1])+'</li></ul>');continue;}
      para.push(line);
    }
    flush();
    return '<div class="explanation-rich">'+blocks.join('')+'</div>';
  }
  window.QB_V103_EXPLANATION=richExplanation;

  function installReview(){
    if(!window.QB || typeof window.QB.reviewTest!=='function') return false;
    window.QB.reviewTest=function(testId){
      try{
        const wanted=decodeURIComponent(String(testId??''));
        const tests=(window.state&&Array.isArray(window.state.tests))?window.state.tests:[];
        const t=tests.find(x=>String(x.id)===wanted);
        if(!t || !Array.isArray(t.questionIds) || !t.questionIds.length){
          console.warn('V103 review: completed test not found',wanted); return false;
        }
        const answers=Object.assign({},t.answers||{});
        const session={id:'review_'+String(t.id),mode:'review',sourceTestId:String(t.id),title:'Review · '+String(t.title||'Completed Test'),questionIds:t.questionIds.slice(),index:0,answers:answers,submitted:Object.fromEntries(t.questionIds.map(id=>[id,Object.prototype.hasOwnProperty.call(answers,id)])),startedAt:t.createdAt||Date.now(),questionTimes:Object.assign({},t.questionTimes||{})};
        window.state.activeSession=session;
        if(typeof window.saveState==='function') window.saveState();
        if(typeof window.navigate==='function') window.navigate('review-test',encodeURIComponent(String(t.id)));
        else location.hash='#review-test/'+encodeURIComponent(String(t.id));
        setTimeout(function(){if(typeof window.render==='function')window.render();},0);
        return false;
      }catch(e){console.error('V103 review navigation failed',e);return false;}
    };
    return true;
  }
  const timer=setInterval(()=>{if(installReview())clearInterval(timer);},50); setTimeout(()=>clearInterval(timer),5000);
  function format(){
    document.querySelectorAll('.feedback-body,.explanation,.explanation-body').forEach(el=>{
      if(el.dataset.v103Formatted==='1') return;
      const txt=el.textContent||''; if(!txt.trim()) return;
      const rich=richExplanation(txt); if(rich){el.innerHTML=rich;el.dataset.v103Formatted='1';}
    });
  }
  new MutationObserver(format).observe(document.documentElement,{childList:true,subtree:true}); format();
})();
</script>
'''

s = s.replace('</head>', css + '</head>', 1)
s = s.replace('</body>', js + '\n' + marker + '\n</body>', 1)
p.write_text(s)
print('overlay applied')
