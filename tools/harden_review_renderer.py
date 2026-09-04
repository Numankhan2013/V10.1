from pathlib import Path
import re

p = Path('app/src/main/assets/index.html')
s = p.read_text(encoding='utf-8')

review_fn = r'''function reviewTestPage(){
    let s=state.activeSession;
    const routeId=(()=>{try{return decodeURIComponent(String(route.id||''));}catch(_){return String(route.id||'');}})();
    if(!s || s.mode!=='review' || (routeId && String(s.sourceTestId)!==routeId)) {
      const t=state.tests.find(x=>String(x.id)===routeId || String(x.id)===String(route.id));
      if(!t) return testsPage();
      s=buildReviewSession(t);
      state.activeSession=s;
      saveState();
    }
    if(!Array.isArray(s.questionIds)||!s.questionIds.length) return testsPage();
    if(!Number.isInteger(s.index)||s.index<0||s.index>=s.questionIds.length) s.index=0;
    const q=BY_ID[s.questionIds[s.index]];
    if(!q) return testsPage();
    const selected=s.answers?.[q.id] ?? null;
    const corr=selected!=null && Number(selected)===Number(q.correctOption);
    const answerText=q.options?.[Number(q.correctOption)-1]?.text || '';
    let explanation='';
    if(q.explanation){
      try{explanation=formatExplanation(q.explanation)||'';}
      catch(e){console.error('Review explanation formatter failed',e);explanation=`<p class="explain-paragraph">${esc(q.explanation)}</p>`;}
    }
    return shell(`
      <div class="page-head"><div><div class="mode-pill">Test Review</div><h1 class="page-title" style="margin-top:9px">${esc(s.title)}</h1><div class="page-sub">Question ${q.questionNumber} of ${s.questionIds.length}</div></div><button class="ghost-btn" onclick="window.QB.nav('tests')">Back to Tests</button></div>
      <section class="card question-card"><div class="crumb">${esc(q.chapter)}</div><div class="question-text">${esc(q.question)}</div><div class="option-list">${(q.options||[]).map(o=>{const n=o.letter.charCodeAt(0)-64,isSel=Number(selected)===n,isCor=Number(q.correctOption)===n;let cls='option';if(isSel)cls+=' selected';if(isCor)cls+=' correct';if(isSel&&!isCor)cls+=' wrong';return `<div class="${cls}"><span class="radio"></span><span class="option-letter">${o.letter}</span><span class="option-text">${esc(o.text)}</span></div>`}).join('')}</div><div class="feedback ${corr?'good':'bad'}"><div class="feedback-title">${selected!=null?(corr?'Correct':'Incorrect'):'Unattempted'}</div><div class="label">Correct answer</div><div style="font-weight:800">${String.fromCharCode(64+Number(q.correctOption))}. ${esc(answerText)}</div>${explanation?`<div class="label">Source explanation</div><div class="feedback-body">${explanation}</div>`:''}</div><div class="q-footer"><button class="ghost-btn" onclick="window.QB.prevQ()">Previous</button><button class="primary-btn" onclick="window.QB.nextQ()">Next ${navIcon('chevron',15)}</button></div><div class="source-box"><details><summary>Source page ${q.sourcePage}</summary><a class="source-link" href="assets/Biochemistry_QBank_Source.pdf#page=${q.sourcePage}" target="_blank">Open original PDF</a></details></div></section>
    `,'tests','Review');
  }'''

s, n = re.subn(r'function reviewTestPage\(\)\{.*?\n  \}\n\n  function endSession\(\)', review_fn + '\n\n  function endSession()', s, count=1, flags=re.S)
if n != 1:
    raise SystemExit(f'Expected one reviewTestPage, got {n}')

# Do not hide a renderer exception behind the generic toast. Keep the click path
# simple and make reviewTest return a useful failure toast only for lookup/data errors.
old = "}catch(e){console.error('Review Solutions failed',e);showToast('Review Solutions could not open.','bad');return false;}"
new = "}catch(e){console.error('Review Solutions failed',e);showToast('Review Solutions error: '+(e?.message||e),'bad');return false;}"
if old in s:
    s = s.replace(old,new,1)

p.write_text(s, encoding='utf-8')
print('Defensive review renderer applied.')
