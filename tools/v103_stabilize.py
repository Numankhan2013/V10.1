from pathlib import Path

INDEX = Path('app/src/main/assets/index.html')
MARKER = 'id="v103-stabilize"'

STYLE = r'''<style id="v103-stabilize">
.review-test .review-nav{margin-top:14px}
.review-test .review-nav-grid{display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:6px;margin-top:10px}
.review-test .review-nav-grid .nav-q{width:100%}
.v103-explain-lead{font-size:15px;line-height:1.72;color:#2f3442;margin:0 0 14px}
.v103-explain-section{margin-top:16px;padding-top:12px;border-top:1px solid #e8eaf0}
.v103-explain-section h4{margin:0 0 8px;font-size:12px;line-height:1.25;letter-spacing:.55px;text-transform:uppercase;color:#4b5270;font-weight:900}
.v103-explain-block{padding:10px 12px;border-radius:12px;background:#fafbfe;border:1px solid #e7e9ef;font-size:14px;line-height:1.65;color:#363d4d}
.v103-explain-list{margin:8px 0 0 20px;padding:0}.v103-explain-list li{margin:0 0 7px;padding-left:2px}
.v103-explain-option{display:grid;grid-template-columns:76px 1fr;gap:10px;padding:10px 0;border-top:1px solid #eceef2}.v103-explain-option:first-child{border-top:0}.v103-explain-option strong{font-size:12px;color:#687084;font-weight:900}.v103-explain-option span{font-size:14px;line-height:1.6;color:#363d4d}
@media(max-width:640px){.review-test .review-nav-grid{grid-template-columns:repeat(5,minmax(0,1fr))}.v103-explain-option{grid-template-columns:60px 1fr}}
</style>'''

SCRIPT = r'''<script id="v103-stabilize">
(function(){
  'use strict';
  const LS='qbank_state_v1';
  const state=()=>{try{return window.QB&&typeof window.QB.getState==='function'?window.QB.getState():null;}catch(_){return null;}};
  const persist=()=>{try{const s=state();if(s)localStorage.setItem(LS,JSON.stringify(s));}catch(_){}};
  const rerender=()=>{try{const href=location.hash||'#dashboard';location.hash='';location.hash=href;}catch(_){location.reload();}};

  function installReviewNavigation(){
    if(!window.QB||window.QB.__v103ReviewWrapped)return false;
    const originalNext=window.QB.nextQ, originalPrev=window.QB.prevQ;
    window.QB.nextQ=function(){
      const s=state();
      if(s&&s.activeSession&&s.activeSession.mode==='review'){
        if(s.activeSession.index < s.activeSession.questionIds.length-1){s.activeSession.index++;persist();rerender();}
        return;
      }
      return originalNext&&originalNext.apply(this,arguments);
    };
    window.QB.prevQ=function(){
      const s=state();
      if(s&&s.activeSession&&s.activeSession.mode==='review'){
        if(s.activeSession.index>0){s.activeSession.index--;persist();rerender();}
        return;
      }
      return originalPrev&&originalPrev.apply(this,arguments);
    };
    window.QB.reviewNext=function(){window.QB.nextQ();};
    window.QB.reviewPrev=function(){window.QB.prevQ();};
    window.QB.reviewIndex=function(i){
      const s=state();if(!s||!s.activeSession||s.activeSession.mode!=='review')return;
      const n=Number(i);if(!Number.isInteger(n)||n<0||n>=s.activeSession.questionIds.length)return;
      s.activeSession.index=n;persist();rerender();
    };
    window.QB.__v103ReviewWrapped=true;
    return true;
  }

  function wireReviewCta(){
    document.addEventListener('click',function(e){
      const el=e.target&&e.target.closest?e.target.closest('[data-v102-review-cta]'):null;
      if(!el||!window.QB||typeof window.QB.reviewTest!=='function')return;
      const id=el.getAttribute('data-review-test-id');if(!id)return;
      e.preventDefault();e.stopImmediatePropagation();window.QB.reviewTest(id);
    },true);
  }

  function structureExplanation(el){
    if(!el||el.dataset.v103Structured==='1')return;
    const raw=(el.textContent||'').replace(/\r/g,'').trim();if(raw.length<160)return;
    const clean=raw.replace(/\s+/g,' ').trim();
    const correct=clean.match(/^Correct Answer\s*:\s*([A-D])[).:\-]?\s*/i);
    const sections=[];
    if(correct){sections.push('<div class="v103-explain-lead"><strong>Correct answer: '+correct[1].toUpperCase()+'</strong></div>');}
    let body=correct?clean.slice(correct[0].length):clean;
    body=body.replace(/\bExplanation\s*:\s*/i,'');
    const optionParts=[];body=body.replace(/(?:^|\s)(Option\s+[A-D]\s*[:.)-]\s*)(.*?)(?=\sOption\s+[A-D]\s*[:.)-]|$)/gi,function(_,label,text){optionParts.push({label:label.trim(),text:text.trim()});return '';});
    const labelRe=/(?:^|\s)([A-Za-z][A-Za-z /&-]{2,38})\s*:\s*/g;
    let last=0,m,found=0,parts=[];while((m=labelRe.exec(body))&&found<8){if(m.index>last)parts.push({text:body.slice(last,m.index).trim()});parts.push({head:m[1].trim()});last=m.index+m[0].length;found++;}if(last<body.length)parts.push({text:body.slice(last).trim()});
    if(parts.length){parts.forEach(p=>{if(p.head)sections.push('<div class="v103-explain-section"><h4>'+esc(p.head)+'</h4>');else if(p.text)sections.push('<div class="v103-explain-block">'+esc(p.text)+'</div></div>');});}
    if(!parts.length&&!sections.length&&body)sections.push('<div class="v103-explain-block">'+esc(body)+'</div>');
    if(optionParts.length){sections.push('<div class="v103-explain-section"><h4>Option analysis</h4>'+optionParts.map(x=>'<div class="v103-explain-option"><strong>'+esc(x.label.replace(/\s+/g,' '))+'</strong><span>'+esc(x.text)+'</span></div>').join('')+'</div>');}
    if(sections.length){el.innerHTML=sections.join('');el.dataset.v103Structured='1';}
  }
  function esc(v){return String(v??'').replace(/[&<>\"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;',"'":'&#39;'}[c]));}
  function structureAll(){document.querySelectorAll('.feedback-body').forEach(structureExplanation);}

  function boot(){
    installReviewNavigation();wireReviewCta();structureAll();
    const mo=new MutationObserver(function(){installReviewNavigation();structureAll();});mo.observe(document.body,{childList:true,subtree:true});
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',boot);else boot();
})();
</script>'''

text = INDEX.read_text(encoding='utf-8')
if MARKER in text:
    print('V10.3 stabilization already present')
else:
    if '</head>' not in text or '</body>' not in text:
        raise SystemExit('index.html missing head/body markers')
    text=text.replace('</head>',STYLE+'\n</head>',1)
    text=text.replace('</body>',SCRIPT+'\n</body>',1)
    INDEX.write_text(text,encoding='utf-8')
    print('Applied V10.3 stabilization overlay')
