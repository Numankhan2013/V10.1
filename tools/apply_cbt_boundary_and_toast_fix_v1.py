from pathlib import Path
import re

HTML = Path('app/src/main/assets/index.html')
s = HTML.read_text(encoding='utf-8')

old_toast = """function showToast(msg,type='') { const root=document.getElementById('toast-root'); const el=document.createElement('div'); el.className='toast '+type; el.textContent=msg; root.appendChild(el); clearTimeout(toastTimer); toastTimer=setTimeout(()=>el.remove(),2600); }"""
new_toast = """function showToast(msg,type='') { const root=document.getElementById('toast-root'); if(!root)return; root.innerHTML=''; clearTimeout(toastTimer); const el=document.createElement('div'); el.className='toast '+type; el.textContent=msg; root.appendChild(el); toastTimer=setTimeout(()=>{root.innerHTML='';},2600); }"""
if s.count(old_toast) != 1:
    raise SystemExit(f'Expected exactly one showToast target, found {s.count(old_toast)}')
s = s.replace(old_toast, new_toast, 1)

old_next = """function nextQ(){ const s=state.activeSession;if(!s)return;if(s.mode==='practice')savePracticeElapsed();else if(s.mode==='exam')saveExamElapsed(); if(s.index<s.questionIds.length-1){s.index++;s.questionEnteredAt=Date.now();saveState();render();}else if(s.mode==='exam'){submitExam(false)}else if(s.mode==='review'){s.index=0;render();}else{showToast('End of session reached.');render();} }"""
new_next = r'''function sessionReviewClass(status){return status?'answered':'unanswered';}
  function openSessionReview(){
    const s=state.activeSession;
    if(!s||!['practice','exam'].includes(s.mode))return;
    if(s.mode==='practice')savePracticeElapsed(); else if(s.mode==='exam')saveExamElapsed();
    const root=document.getElementById('toast-root');if(root)root.innerHTML='';
    document.getElementById('nk-session-review')?.remove();
    const total=s.questionIds.length;
    const answered=s.questionIds.reduce((n,id)=>n+(s.answers[id]?1:0),0);
    const unanswered=total-answered;
    const heading=s.mode==='exam'?'Review before submitting':'Review before finishing';
    const sub=s.mode==='exam'
      ? 'Check answered, skipped, and unanswered questions. You can jump back to any question before submitting the test.'
      : 'Check the questions you answered and jump back to any unanswered question before finishing the session.';
    const actionLabel=s.mode==='exam'?'Submit Test':'Finish Session';
    const statusText=unanswered?
      `${answered} answered · ${unanswered} unanswered`:
      `${answered} answered · all questions covered`;
    const cells=s.questionIds.map((id,i)=>{
      const q=BY_ID[id],answeredQ=Boolean(s.answers[id]);
      return `<button type="button" class="nk-session-review-q ${sessionReviewClass(answeredQ)} ${i===s.index?'active':''}" onclick="window.QB.__sessionReviewGo(${i})" aria-label="Question ${q?.questionNumber||i+1}${answeredQ?' answered':' unanswered'}"><span>${q?.questionNumber||i+1}</span><small>${answeredQ?'Answered':'Unanswered'}</small></button>`;
    }).join('');
    const unansweredBtn=unanswered
      ? `<button type="button" class="ghost-btn" onclick="window.QB.__sessionReviewFirstUnanswered()">Review unanswered</button>`
      : `<button type="button" class="ghost-btn" onclick="window.QB.__sessionReviewGo(${Math.max(0,s.index)})">Back to question</button>`;
    const backBtn=unanswered
      ? `<button type="button" class="ghost-btn" onclick="window.QB.__sessionReviewGo(${Math.max(0,s.index)})">Back to question</button>`
      : '';
    const box=document.createElement('div');
    box.id='nk-session-review';
    box.className='nk-session-review-backdrop';
    box.innerHTML=`<section class="nk-session-review-card" role="dialog" aria-modal="true" aria-label="${heading}">
      <div class="nk-session-review-head"><div><div class="mode-pill">${s.mode==='exam'?'Exam':'Practice'} · Session Review</div><h2>${heading}</h2><p>${sub}</p></div><button type="button" class="icon-btn nk-session-review-close" aria-label="Close" onclick="window.QB.__sessionReviewClose()">×</button></div>
      <div class="nk-session-review-summary"><strong>${statusText}</strong><span>${total} questions</span></div>
      <div class="nk-session-review-grid">${cells}</div>
      <div class="nk-session-review-legend"><span><i class="nk-review-dot answered"></i>Answered</span><span><i class="nk-review-dot unanswered"></i>Unanswered</span><span><i class="nk-review-dot active"></i>Current</span></div>
      <div class="nk-session-review-actions${unanswered?'':' two'}">${backBtn}${unansweredBtn}<button type="button" class="primary-btn" onclick="window.QB.__sessionReviewSubmit()">${actionLabel}</button></div>
      ${unanswered?`<div class="nk-session-review-warning">${unanswered} question${unanswered===1?'':'s'} remain unanswered. You can review them now or submit/finish with them left blank.</div>`:`<div class="nk-session-review-ready">All questions have an answer. You can submit/finish this session.</div>`}
    </section>`;
    document.body.appendChild(box);
  }
  function closeSessionReview(){document.getElementById('nk-session-review')?.remove();}
  function sessionReviewGo(i){const s=state.activeSession;if(!s||i<0||i>=s.questionIds.length)return;s.index=i;s.questionEnteredAt=Date.now();saveState();closeSessionReview();render();}
  function sessionReviewFirstUnanswered(){const s=state.activeSession;if(!s)return;const i=s.questionIds.findIndex(id=>!s.answers[id]);if(i>=0)sessionReviewGo(i);}
  function sessionReviewSubmit(){const s=state.activeSession;if(!s)return;closeSessionReview();if(s.mode==='exam')submitExam(false);else endSession();}
  function nextQ(){ const s=state.activeSession;if(!s)return;if(s.mode==='practice')savePracticeElapsed();else if(s.mode==='exam')saveExamElapsed(); if(s.index<s.questionIds.length-1){s.index++;s.questionEnteredAt=Date.now();saveState();render();}else if(s.mode==='practice'||s.mode==='exam'){openSessionReview();}else if(s.mode==='review'){s.index=0;render();} }'''
if s.count(old_next) != 1:
    raise SystemExit(f'Expected exactly one nextQ target, found {s.count(old_next)}')
s = s.replace(old_next, new_next, 1)

css = r'''
<style id="nk-cbt-boundary-fix-v1">
.nk-session-review-backdrop{position:fixed;inset:0;z-index:95;background:rgba(22,23,38,.46);backdrop-filter:blur(8px);display:grid;place-items:center;padding:14px;overflow:auto}
.nk-session-review-card{width:min(620px,100%);max-height:min(88vh,820px);overflow:auto;background:var(--surface);border:1px solid var(--line);border-radius:22px;box-shadow:0 28px 90px rgba(0,0,0,.25);padding:18px}
.nk-session-review-head{display:flex;align-items:flex-start;justify-content:space-between;gap:12px}.nk-session-review-head h2{margin:8px 0 6px;font-size:22px}.nk-session-review-head p{margin:0;color:var(--muted);font-size:13px;line-height:1.5;max-width:520px}.nk-session-review-close{color:var(--ink);border:1px solid var(--line);background:#f7f7fb;font-size:22px}
.nk-session-review-summary{display:flex;justify-content:space-between;gap:10px;align-items:center;margin:16px 0 12px;padding:12px 13px;border:1px solid var(--line);border-radius:14px;background:#fafbff}.nk-session-review-summary strong{font-size:14px}.nk-session-review-summary span{font-size:12px;color:var(--muted)}
.nk-session-review-grid{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:8px}.nk-session-review-q{border:1px solid var(--line);background:#fff;border-radius:12px;min-height:58px;padding:7px 4px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:2px;color:#767887}.nk-session-review-q span{font-size:14px;font-weight:820}.nk-session-review-q small{font-size:8px;line-height:1.1}.nk-session-review-q.answered{background:#eef5ff;border-color:#c8d6fb;color:var(--primary)}.nk-session-review-q.unanswered{background:#fff}.nk-session-review-q.active{box-shadow:0 0 0 2px var(--primary);border-color:var(--primary);color:var(--primary)}
.nk-session-review-legend{display:flex;gap:14px;flex-wrap:wrap;margin:13px 0 15px;color:var(--muted);font-size:10px}.nk-review-dot{display:inline-block;width:9px;height:9px;border-radius:3px;border:1px solid var(--line);vertical-align:middle;margin-right:5px}.nk-review-dot.answered{background:#eef5ff;border-color:#c8d6fb}.nk-review-dot.unanswered{background:#fff}.nk-review-dot.active{background:var(--primary);border-color:var(--primary)}
.nk-session-review-actions{display:grid;grid-template-columns:1fr 1fr 1fr;gap:9px}.nk-session-review-actions.two{grid-template-columns:1fr 1fr}.nk-session-review-actions>*{width:100%}.nk-session-review-warning,.nk-session-review-ready{margin-top:11px;padding:10px 12px;border-radius:11px;font-size:11px;line-height:1.45}.nk-session-review-warning{background:#fff7e7;color:#7e5b18;border:1px solid #f0ddb0}.nk-session-review-ready{background:#effbf6;color:#25745e;border:1px solid #bce4d5}
@media(max-width:640px){.nk-session-review-backdrop{padding:10px}.nk-session-review-card{padding:15px;border-radius:18px}.nk-session-review-grid{gap:6px}.nk-session-review-q{min-height:54px}.nk-session-review-actions{grid-template-columns:1fr 1fr}.nk-session-review-actions .primary-btn{grid-column:1/-1;order:-1}}
</style>
'''
if 'id="nk-cbt-boundary-fix-v1"' not in s:
    s=s.replace('</head>',css+'</head>',1)

# Wire the lexical session-review helpers into the main public QB object only after
# all helper functions have been inserted. This avoids being overwritten by the
# original window.QB assignment later in the same script.
if 'window.QB.openSessionReview=openSessionReview' not in s:
    m = re.search(r'window\.QB=\{([^\n]+)\};', s)
    if not m:
        raise SystemExit('Could not locate canonical window.QB object assignment')
    body = m.group(1)
    if 'sessionReviewGo' not in body:
        body += ',__sessionReviewGo:sessionReviewGo,__sessionReviewFirstUnanswered:sessionReviewFirstUnanswered,__sessionReviewClose:closeSessionReview,__sessionReviewSubmit:sessionReviewSubmit,openSessionReview:openSessionReview'
        s = s[:m.start(1)] + body + s[m.end(1):]

HTML.write_text(s,encoding='utf-8')
print('CBT boundary flow + singleton toast fix installed.')
