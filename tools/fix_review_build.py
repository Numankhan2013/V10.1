from pathlib import Path
import re

p = Path('app/src/main/assets/index.html')
s = p.read_text(encoding='utf-8')

for script_id in ('v103-stabilize', 'v103-review-explanation-js', 'v1033-review-hardening'):
    s = re.sub(rf'\n?<script id="{re.escape(script_id)}">.*?</script>\n?', '\n', s, count=1, flags=re.S)
s = s.replace('<!-- V1033_REVIEW_HARDENING -->', '')
s = re.sub(r'\n  function reviewSolutionsGuard\(\)\{.*?\n  reviewSolutionsGuard\(\);\n', '\n', s, count=1, flags=re.S)

old = '<button class="primary-btn v102-review-action" type="button" data-v102-review-cta="1" data-review-test-id="${esc(t.id)}">Review Solutions</button>'
new = '<button class="primary-btn v102-review-action" type="button" data-review-test-id="${esc(t.id)}" onclick="window.QB.reviewTest(this.getAttribute(\'data-review-test-id\'))">Review Solutions</button>'
s = s.replace(old, new, 1)
s = s.replace('data-v102-review-cta="1" data-review-test-id="${esc(t.id)}"', 'data-review-test-id="${esc(t.id)}" onclick="window.QB.reviewTest(this.getAttribute(\'data-review-test-id\'))"', 1)

# Make the review-session constructor compatible with older Android WebViews.
s = s.replace(
    "submitted:Object.fromEntries(t.questionIds.map(id=>[id,Boolean(t.answers?.[id])]))",
    "submitted:t.questionIds.reduce((a,id)=>{a[id]=Boolean(t.answers&&t.answers[id]);return a;},{})",
    1,
)

# Replace the review opener with a minimal, staged implementation. Any failure is
# surfaced with the exact stage so the physical device cannot hide the root cause.
start = s.find('function reviewTest(testId){')
end = s.find('function reviewTestPage(){', start)
if start >= 0 and end > start:
    replacement = '''function reviewTest(testId){
      let stage='lookup';
      try{
        let wanted=String(testId==null?'':testId);
        try{wanted=decodeURIComponent(wanted);}catch(_){stage='lookup-decode';}
        const tests=Array.isArray(state.tests)?state.tests:[];
        const t=tests.find(x=>String(x.id)===wanted || String(x.id)===String(testId));
        if(!t){showToast('That completed test could not be found.','bad');return false;}
        if(!Array.isArray(t.questionIds)||!t.questionIds.length){showToast('This test has no saved questions to review.','bad');return false;}
        stage='session';
        const session=buildReviewSession(t);
        session.questionEnteredAt=Date.now();
        state.activeSession=session;
        stage='save';
        saveState();
        stage='route';
        route={page:'review-test',id:String(t.id)};
        stage='render';
        render();
        stage='history';
        try{history.replaceState(null,'',`#review-test/${encodeURIComponent(String(t.id))}`);}catch(_){location.hash=`#review-test/${encodeURIComponent(String(t.id))}`;}
        return true;
      }catch(e){
        console.error('Review Solutions failed at '+stage,e);
        showToast('Review Solutions failed at '+stage+'.','bad');
        return false;
      }
    }
    '''
    s = s[:start] + replacement + s[end:]

# Remove the permanent in-page question navigator. It will be opened on demand from the More menu.
s = re.sub(r'<aside class="card navigator">.*?</aside>', '', s, flags=re.S)
s = re.sub(r'\n\s*const navItems=s\.questionIds\.map\(\(id,i\)=>\{.*?\}\)\.join\(\'\'\);', '', s, count=1)
s = re.sub(r'\n\s*const navItems=s\.questionIds\.map\(\(id,i\)=>\{.*?\}\)\.join\(\'\'\);', '', s, count=1)

# Add a four-circle navigator icon and route all question-page More buttons through the compact tools menu.
needle = '      more:`<svg ${common}><circle cx="5" cy="12" r="1"/><circle cx="12" cy="12" r="1"/><circle cx="19" cy="12" r="1"/></svg>`,\n'
insert = needle + '      grid:`<svg ${common}><circle cx="7" cy="7" r="2.1"/><circle cx="17" cy="7" r="2.1"/><circle cx="7" cy="17" r="2.1"/><circle cx="17" cy="17" r="2.1"/></svg>`,\n'
s = s.replace(needle, insert, 1)
s = s.replace('onclick="window.QB.notify()">${navIcon(\'more\')}', 'onclick="window.QB.openQuestionTools(this)">${navIcon(\'more\')}', 3)

# Review gets the same More control without changing its content structure.
old_review = '<section class="card question-card"><div class="crumb">${esc(q.chapter)}</div>'
new_review = '<section class="card question-card"><div class="q-head"><div class="q-number">Question ${q.questionNumber} of ${s.questionIds.length}</div><div class="q-actions"><button class="icon-btn" aria-label="More" onclick="window.QB.openQuestionTools(this)">${navIcon(\'more\')}</button></div></div><div class="crumb">${esc(q.chapter)}</div>'
s = s.replace(old_review, new_review, 1)

# Inject navigator menu/modal behavior before endSession.
marker = '  function endSession() { state.activeSession=null; saveState(); navigate(\'dashboard\'); }'
block = r'''  function closeQuestionTools(){ document.getElementById('qb-question-tools')?.remove(); }
  function closeQuestionNavigator(){ document.getElementById('qb-question-navigator')?.remove(); }
  function openQuestionTools(anchor){
    closeQuestionTools();
    const r=anchor?.getBoundingClientRect ? anchor.getBoundingClientRect() : null;
    const top=r ? Math.min(window.innerHeight-86, Math.max(10,r.bottom+8)) : 80;
    const right=r ? Math.max(10,window.innerWidth-r.right) : 14;
    document.body.insertAdjacentHTML('beforeend',`<div class="qb-tools-pop" id="qb-question-tools" style="top:${top}px;right:${right}px" role="menu">
      <button type="button" class="qb-tools-item" role="menuitem" onclick="window.QB.openQuestionNavigator()"><span class="qb-tools-icon">${navIcon('grid',20)}</span><span><strong>Question Navigator</strong><small>Jump to any question</small></span></button>
    </div>`);
    setTimeout(()=>{const pop=document.getElementById('qb-question-tools');if(!pop)return;const close=e=>{if(!pop.contains(e.target)&&e.target!==anchor){closeQuestionTools();document.removeEventListener('click',close);}};document.addEventListener('click',close);},0);
  }
  function openQuestionNavigator(){
    closeQuestionTools(); closeQuestionNavigator();
    const s=state.activeSession;
    if(!s||!Array.isArray(s.questionIds)||!s.questionIds.length){showToast('No active question session.','bad');return;}
    const review=s.mode==='review';
    const items=s.questionIds.map((id,i)=>{
      const q=BY_ID[id]; if(!q)return '';
      const val=s.answers&&s.answers[id], submitted=Boolean(s.submitted&&s.submitted[id]);
      let cls=i===s.index?'active ':'';
      if(review||s.mode==='practice'){
        if(submitted) cls += Number(q.correctOption)===Number(val)?'correct ':'incorrect ';
        else if(val) cls+='answered ';
      } else if(val) cls+='answered ';
      if(state.bookmarks&&state.bookmarks[id]) cls+='bookmarked ';
      return `<button type="button" class="qb-nav-q ${cls}" onclick="window.QB.jumpFromNavigator(${i})" aria-label="Question ${q.questionNumber}"><span>${q.questionNumber}</span></button>`;
    }).join('');
    const legend=review||s.mode==='practice'
      ? '<span><i class="qb-legend-dot current"></i>Current</span><span><i class="qb-legend-dot answered"></i>Answered</span><span><i class="qb-legend-dot correct"></i>Correct</span><span><i class="qb-legend-dot incorrect"></i>Incorrect</span><span><i class="qb-legend-dot unanswered"></i>Unanswered</span>'
      : '<span><i class="qb-legend-dot current"></i>Current</span><span><i class="qb-legend-dot answered"></i>Answered</span><span><i class="qb-legend-dot unanswered"></i>Unanswered</span>';
    document.body.insertAdjacentHTML('beforeend',`<div class="qb-nav-backdrop" id="qb-question-navigator" role="dialog" aria-modal="true" aria-labelledby="qb-nav-title">
      <div class="qb-nav-panel">
        <div class="qb-nav-head"><div><div class="qb-nav-eyebrow">${esc(s.mode==='review'?'Test Review':s.mode==='exam'?'Exam Mode':'Practice Mode')}</div><h3 id="qb-nav-title">Question Navigator</h3><p>${s.questionIds.length} questions · tap a number to jump</p></div><button type="button" class="qb-nav-close" aria-label="Close" onclick="window.QB.closeQuestionNavigator()">${navIcon('close',20)}</button></div>
        <div class="qb-nav-grid">${items}</div>
        <div class="qb-nav-legend">${legend}</div>
      </div>
    </div>`);
  }
  function jumpFromNavigator(i){ closeQuestionNavigator(); goIndex(i); }
'''
s = s.replace(marker, block + '\n' + marker, 1)

# Expose the new navigator controls.
s = s.replace('window.QB={getState:()=>state,nav:navigate,setSubject,toggleMenu,notify,', 'window.QB={getState:()=>state,nav:navigate,setSubject,toggleMenu,notify,openQuestionTools,openQuestionNavigator,closeQuestionNavigator,jumpFromNavigator,')

# New compact menu + overlay styling. Hide the old permanent navigator in case an older renderer leaves one behind.
style_marker = '</style>'
styles = r'''
.qb-tools-pop{position:fixed;z-index:110;min-width:235px;padding:7px;border:1px solid var(--line);border-radius:15px;background:#fff;box-shadow:0 18px 50px rgba(25,27,48,.18);animation:fadeIn .12s ease}.qb-tools-item{display:flex;align-items:center;gap:11px;width:100%;padding:10px 11px;border:0;border-radius:11px;background:#fff;text-align:left;color:var(--ink)}.qb-tools-item:hover{background:#f6f7fb}.qb-tools-icon{width:36px;height:36px;display:grid;place-items:center;border-radius:10px;background:#eef0fa;color:var(--primary)}.qb-tools-item strong{display:block;font-size:12px;font-weight:850}.qb-tools-item small{display:block;margin-top:2px;color:var(--muted);font-size:10px}.qb-nav-backdrop{position:fixed;inset:0;z-index:108;background:rgba(20,22,38,.42);backdrop-filter:blur(7px);-webkit-backdrop-filter:blur(7px);display:grid;place-items:end center;padding:14px}.qb-nav-panel{width:min(720px,100%);max-height:min(82vh,760px);overflow:auto;background:#fff;border-radius:24px;padding:18px;box-shadow:0 30px 90px rgba(0,0,0,.24);animation:fadeIn .16s ease}.qb-nav-head{display:flex;align-items:flex-start;justify-content:space-between;gap:12px;margin-bottom:14px}.qb-nav-eyebrow{font-size:10px;font-weight:850;letter-spacing:.7px;text-transform:uppercase;color:var(--primary-2)}.qb-nav-head h3{margin:3px 0 4px;font-size:21px;font-weight:900}.qb-nav-head p{margin:0;color:var(--muted);font-size:11px}.qb-nav-close{width:42px;height:42px;display:grid;place-items:center;border:1px solid var(--line);border-radius:13px;background:#fff;color:#626878}.qb-nav-grid{display:grid;grid-template-columns:repeat(8,1fr);gap:8px}.qb-nav-q{position:relative;aspect-ratio:1;border:1px solid #dfe2ea;border-radius:11px;background:#fff;color:#606575;font-size:12px;font-weight:850}.qb-nav-q.active{border-color:var(--primary);background:#eef0fa;color:var(--primary);box-shadow:0 0 0 2px rgba(47,45,99,.09)}.qb-nav-q.answered{background:#eef4ff;border-color:#c7d5f7}.qb-nav-q.correct{background:#effbf6;border-color:#8dd6bd;color:var(--success)}.qb-nav-q.incorrect{background:#fff3f3;border-color:#edb5b8;color:var(--danger)}.qb-nav-q.bookmarked:after{content:'';position:absolute;right:4px;top:4px;width:5px;height:5px;border-radius:50%;background:var(--warning)}.qb-nav-legend{display:flex;flex-wrap:wrap;gap:9px 15px;margin-top:14px;padding-top:12px;border-top:1px solid var(--line);color:var(--muted);font-size:10px}.qb-legend-dot{display:inline-block;width:9px;height:9px;border-radius:3px;border:1px solid var(--line);margin-right:5px;vertical-align:middle}.qb-legend-dot.current{background:#eef0fa;border-color:#aaaed0}.qb-legend-dot.answered{background:#eef4ff}.qb-legend-dot.correct{background:#effbf6}.qb-legend-dot.incorrect{background:#fff3f3}.qb-legend-dot.unanswered{background:#fff}
@media(max-width:640px){.qb-tools-pop{min-width:225px}.qb-nav-backdrop{padding:10px}.qb-nav-panel{padding:15px;border-radius:22px;max-height:86vh}.qb-nav-grid{grid-template-columns:repeat(6,1fr);gap:6px}.qb-nav-q{border-radius:9px;font-size:11px}.qb-nav-legend{gap:7px 11px}}
'''
s = s.replace(style_marker, styles + '\n' + style_marker, 1)

p.write_text(s, encoding='utf-8')
print('Navigator redesign applied.')
