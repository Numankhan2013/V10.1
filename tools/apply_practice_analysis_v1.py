from pathlib import Path
import re

HTML = Path('app/src/main/assets/index.html')
s = HTML.read_text(encoding='utf-8')

# Idempotent layer.
s = re.sub(r'<style id="qbank-practice-analysis-v1">.*?</style>\s*', '', s, flags=re.S)

old_end = "function endSession() { state.activeSession=null; saveState(); navigate('dashboard'); }"
new_end = r'''function finishPracticeSession() {
    const s=state.activeSession;
    if(!s || s.mode!=='practice') return;
    savePracticeElapsed();
    const qt={...(s.questionTimes||{})}, answers={...(s.answers||{})};
    let correct=0, incorrect=0, attempted=0;
    Object.entries(answers).forEach(([id,sel])=>{
      if(!sel) return;
      attempted++;
      const q=BY_ID[id];
      if(q && Number(q.correctOption)===Number(sel)) correct++; else incorrect++;
    });
    const total=s.questionIds.length;
    const unattempted=Math.max(0,total-attempted);
    const totalTimeMs=Object.values(qt).reduce((a,b)=>a+(Number(b)||0),0);
    const test={
      id:`p_${Date.now()}_${Math.random().toString(16).slice(2)}`,
      title:s.title,
      kind:'practice',
      questionIds:[...s.questionIds],
      answers,
      questionTimes:qt,
      correct, incorrect, unattempted, total, attempted,
      totalTimeMs, createdAt:Date.now(), autoSubmitted:false
    };
    state.tests.push(test);
    state.tests=state.tests.slice(-100);
    state.activeSession=null;
    saveState();
    document.querySelectorAll('#toast-root .toast').forEach(e=>e.remove());
    navigate('result',test.id);
  }

  function endSession() {
    const s=state.activeSession;
    if(!s) return;
    if(s.mode==='practice'){ finishPracticeSession(); return; }
    state.activeSession=null; saveState(); navigate('dashboard');
  }'''
if old_end not in s:
    raise SystemExit('Expected endSession implementation not found')
s = s.replace(old_end, new_end, 1)

old_result = '''<div class="page-head"><div><button class="ghost-btn" onclick="window.QB.nav('tests')" style="margin-bottom:8px">${navIcon('back',16)} Tests</button><h1 class="page-title">Test Analysis</h1><div class="page-sub">${esc(t.title)} · ${fmtDate(t.createdAt)}</div></div><button class="primary-btn v102-review-action" type="button" data-review-test-id="${esc(t.id)}" onclick="return window.__QB_OPEN_REVIEW(this.getAttribute('data-review-test-id'))">Review Solutions</button></div>'''
new_result = '''<div class="page-head"><div><button class="ghost-btn" onclick="window.QB.nav('tests')" style="margin-bottom:8px">${navIcon('back',16)} Tests</button><div class="mode-pill">${isPractice ? navIcon('book',13)+' Practice Session' : navIcon('test',13)+' Timed CBT'}</div><h1 class="page-title" style="margin-top:8px">${isPractice?'Practice Analysis':'Test Analysis'}</h1><div class="page-sub">${esc(t.title)} · ${fmtDate(t.createdAt)}</div></div><button class="primary-btn v102-review-action" type="button" data-review-test-id="${esc(t.id)}" onclick="return window.__QB_OPEN_REVIEW(this.getAttribute('data-review-test-id'))">Review Solutions</button></div>'''
if old_result not in s:
    raise SystemExit('Expected result page header not found')
s = s.replace(old_result, new_result, 1)

# Add practice discriminator immediately after the result lookup line.
old_lookup = "const t=state.tests.find(x=>x.id===testId); if(!t) return testsPage();\n    const score="
new_lookup = "const t=state.tests.find(x=>x.id===testId); if(!t) return testsPage();\n    const isPractice=t.kind==='practice';\n    const score="
if old_lookup not in s:
    raise SystemExit('Expected result lookup not found')
s = s.replace(old_lookup, new_lookup, 1)

old_stats = '''<div class="grid grid-4" style="margin-top:14px"><div class="card stat-card"><div class="label">Time Taken</div><div class="value">${formatDuration(t.totalTimeMs)}</div><div class="small-muted">${fmtNum(t.questionIds.length)} questions</div></div><div class="card stat-card"><div class="label">Avg. time / attempted</div><div class="value">${formatDuration(t.attempted?attemptedQuestionTime/t.attempted:0)}</div><div class="small-muted">Selected answers only</div></div><div class="card stat-card"><div class="label">Avg. time / question</div><div class="value">${formatDuration(t.total?totalQuestionTime/t.total:0)}</div><div class="small-muted">Includes skips</div></div><div class="card stat-card"><div class="label">Completion</div><div class="value">${fmtPct(t.total?attempted/t.total*100:0)}</div><div class="small-muted">Questions attempted</div></div></div>'''
new_stats = '''<div class="result-stat-grid" style="margin-top:14px">
        <div class="card stat-card result-stat result-stat-time"><div class="result-stat-head"><span class="result-stat-icon">${navIcon('clock',18)}</span><span class="label">Time Taken</span></div><div class="value">${formatDuration(t.totalTimeMs)}</div><div class="small-muted">${fmtNum(t.questionIds.length)} questions</div></div>
        <div class="card stat-card result-stat result-stat-attempted"><div class="result-stat-head"><span class="result-stat-icon">${navIcon('chart',18)}</span><span class="label">Avg. time / attempted</span></div><div class="value">${formatDuration(t.attempted?attemptedQuestionTime/t.attempted:0)}</div><div class="small-muted">Selected answers only</div></div>
        <div class="card stat-card result-stat result-stat-question"><div class="result-stat-head"><span class="result-stat-icon">${navIcon('book',18)}</span><span class="label">Avg. time / question</span></div><div class="value">${formatDuration(t.total?totalQuestionTime/t.total:0)}</div><div class="small-muted">Includes skips</div></div>
        <div class="card stat-card result-stat result-stat-completion"><div class="result-stat-head"><span class="result-stat-icon">${navIcon('check',18)}</span><span class="label">Completion</span></div><div class="value">${fmtPct(t.total?attempted/t.total*100:0)}</div><div class="stat-progress" aria-label="${fmtPct(t.total?attempted/t.total*100:0)} complete"><span style="width:${Math.max(0,Math.min(100,t.total?attempted/t.total*100:0))}%"></span></div><div class="small-muted">Questions attempted</div></div>
      </div>'''
if old_stats not in s:
    raise SystemExit('Expected result stats block not found')
s = s.replace(old_stats, new_stats, 1)

# Remove the large artificial practice spacer; keep source traceability itself.
css = r'''<style id="qbank-practice-analysis-v1">
/* Keep the collapsed source-traceability row close to the options. The fixed
   practice toolbar and page bottom padding already reserve navigation space. */
.practice-actions ~ .bottom-nav + * { }
.question-card .action-spacer { height: 12px !important; }

/* Result stats: same data, clearer visual semantics. */
.result-stat-grid { display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:14px; }
.result-stat { min-height:126px !important; padding:14px !important; }
.result-stat-head { display:flex; align-items:center; gap:9px; min-height:26px; }
.result-stat-head .label { margin:0; font-size:12px !important; font-weight:750 !important; color:#6f7180 !important; }
.result-stat-icon { width:31px; height:31px; border-radius:10px; display:grid; place-items:center; flex:none; }
.result-stat-icon svg { width:18px; height:18px; }
.result-stat .value { margin-top:10px; }
.result-stat-time .result-stat-icon { background:#eef0fa; color:#3d65d8; }
.result-stat-attempted .result-stat-icon { background:#eef7ff; color:#3977ad; }
.result-stat-question .result-stat-icon { background:#f3f0fb; color:#6c55a8; }
.result-stat-completion .result-stat-icon { background:#eaf8f3; color:#159a74; }
.stat-progress { height:5px; border-radius:999px; background:#eceef4; overflow:hidden; margin:10px 0 7px; }
.stat-progress > span { display:block; height:100%; border-radius:inherit; background:var(--success); }
@media(max-width:900px){ .result-stat-grid{grid-template-columns:1fr 1fr;} }
@media(max-width:430px){ .result-stat-grid{gap:10px;} .result-stat{min-height:116px !important;padding:12px !important;} .result-stat-head .label{font-size:10px !important;} .result-stat .value{font-size:20px !important;} .result-stat-icon{width:28px;height:28px;} }
</style>'''
if '</head>' not in s:
    raise SystemExit('Cannot apply practice analysis style: </head> missing')
s = s.replace('</head>', css+'\n</head>', 1)
HTML.write_text(s, encoding='utf-8')
print('Practice analysis v1 applied.')