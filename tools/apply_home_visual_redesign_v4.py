from pathlib import Path
import re

INDEX = Path('app/src/main/assets/index.html')
MAIN = Path('app/src/main/java/com/qbank/biochemistry/MainActivity.java')

# V4 is deliberately applied to the generated app itself. The previous Home
# iterations relied on runtime WebView injection, which made the build look
# unchanged on-device. This step makes the Home composition deterministic.

DASHBOARD = r'''function dashboard() {
    const attempted=totalAttempted(), total=QUESTIONS.length, acc=overallAccuracy();
    const tests=state.tests.length, due=pendingReviewCount(), wrong=wrongQuestions().length, bm=bookmarkedQuestions().length;
    const recent=state.tests.slice().sort((a,b)=>b.createdAt-a.createdAt).slice(0,3);
    const perf=chapterPerformanceRows();
    const focus = due ? `Review ${due} question${due===1?'':'s'} due today.` : wrong ? `Revisit ${wrong} missed question${wrong===1?'':'s'}.` : attempted<total ? 'Build today’s recall with a focused 20-question set.' : 'Your bank is fully in motion — keep sharpening recall.';
    return shell(`
      <div class="nk-home-v4">
        <header class="nk-home-v4-head">
          <div class="nk-home-v4-heading">
            <div class="nk-home-v4-kicker">${esc(activeSubject)} · Personal QBank</div>
            <h1>${greetingCopy()}</h1>
            <p>What are you working on today?</p>
          </div>
          <button class="nk-home-v4-continue" onclick="window.QB.continuePractice()">Continue <span>→</span></button>
        </header>
        <section class="nk-home-v4-today">
          <div class="nk-home-v4-today-copy"><div class="nk-home-v4-label">TODAY'S FOCUS</div><h2>${esc(focus)}</h2><p>${due?'Strengthen what is due before moving on.':wrong?'Turn mistakes into another retrieval opportunity.':'A small, focused set is enough to keep momentum.'}</p></div>
          <div class="nk-home-v4-actions">
            ${due?`<button class="nk-home-v4-primary" onclick="window.QB.startLibrary('review')">Review ${fmtNum(due)} <span>→</span></button>`:`<button class="nk-home-v4-primary" onclick="window.QB.startAllPractice()">Practice 20 <span>→</span></button>`}
            <button class="nk-home-v4-secondary" onclick="window.QB.openTestBuilder()">Timed CBT <span>↗</span></button>
          </div>
        </section>
        <section class="nk-home-v4-section nk-home-v4-subjects">
          <div class="nk-home-v4-section-head"><div><div class="nk-home-v4-label">STUDY LIBRARY</div><h2>Subjects</h2></div><span>${fmtNum(SUBJECTS.length)} available</span></div>
          <div class="nk-home-v4-subject-list">
            ${SUBJECTS.map((x,i)=>{
              const q=QUESTIONS.filter(v=>v.subject===x.subject), done=q.filter(v=>state.answers&&state.answers[v.id]).length, pct=q.length?Math.round(done/q.length*100):0;
              return `<button type="button" class="nk-home-v4-subject ${x.subject===activeSubject?'is-active':''}" onclick="window.QB.setSubject('${esc(x.subject)}')"><span class="nk-home-v4-subject-index">${String(i+1).padStart(2,'0')}</span><span class="nk-home-v4-subject-main"><strong>${esc(x.subject)}</strong><small>${fmtNum(x.questions||q.length)} questions · ${fmtNum(x.topics||0)} topics</small><span class="nk-home-v4-progress"><i style="width:${Math.max(0,Math.min(100,pct))}%"></i></span></span><span class="nk-home-v4-subject-pct">${pct}%</span><span class="nk-home-v4-chevron">→</span></button>`;
            }).join('')}
          </div>
        </section>
        <section class="nk-home-v4-section">
          <div class="nk-home-v4-section-head"><div><div class="nk-home-v4-label">YOUR PROGRESS</div><h2>At a glance</h2></div><button class="nk-home-v4-link" onclick="window.QB.nav('analytics')">Insights →</button></div>
          <div class="nk-home-v4-metrics">
            <div><b>${fmtNum(attempted)}</b><span>Questions</span><small>of ${fmtNum(total)}</small></div>
            <div><b>${fmtPct(acc)}</b><span>Accuracy</span><small>all attempts</small></div>
            <div><b>${fmtNum(due)}</b><span>Due</span><small>review now</small></div>
            <div><b>${fmtNum(tests)}</b><span>Tests</span><small>completed</small></div>
          </div>
        </section>
        <section class="nk-home-v4-section nk-home-v4-tools">
          <div class="nk-home-v4-section-head"><div><div class="nk-home-v4-label">QUICK ACCESS</div><h2>Keep going</h2></div></div>
          <div class="nk-home-v4-tool-grid">
            <button onclick="window.QB.nav('wrong')"><span>Wrong questions</span><small>${fmtNum(wrong)} to revisit</small><b>→</b></button>
            <button onclick="window.QB.nav('review')"><span>Spaced review</span><small>${fmtNum(due)} due today</small><b>→</b></button>
            <button onclick="window.QB.nav('bookmarks')"><span>Bookmarks</span><small>${fmtNum(bm)} saved</small><b>→</b></button>
            <button onclick="window.QB.nav('topics')"><span>Browse topics</span><small>Find your next chapter</small><b>→</b></button>
          </div>
        </section>
        <section class="nk-home-v4-section nk-home-v4-lower">
          <div class="nk-home-v4-two-col">
            <div><div class="nk-home-v4-section-head"><div><div class="nk-home-v4-label">PERFORMANCE</div><h2>Strongest chapters</h2></div><button class="nk-home-v4-link" onclick="window.QB.nav('topics')">All →</button></div>
              ${perf.length?perf.slice(0,4).map(({c,s},i)=>`<div class="nk-home-v4-chapter"><span>${i+1}</span><div><strong>${esc(c.title)}</strong><small>${s.attempted}/${s.total} attempted · ${s.correct} correct</small></div><b>${fmtPct(s.accuracy)}</b></div>`).join(''):`<div class="nk-home-v4-empty">Complete a few questions to build your chapter picture.</div>`}
            </div>
            <div><div class="nk-home-v4-section-head"><div><div class="nk-home-v4-label">RECENT</div><h2>Tests</h2></div><button class="nk-home-v4-link" onclick="window.QB.nav('tests')">All →</button></div>
              ${recent.length?recent.map(testRow).join(''):`<div class="nk-home-v4-empty">Your completed CBTs will appear here.</div>`}
            </div>
          </div>
        </section>
      </div>`, 'dashboard');
  }

'''

CSS = r'''<style id="nk-home-v4-style">
/* NK HOME V4 — composition-first dashboard, intentionally unlike the card-stack Home */
.nk-home-v4{max-width:1040px;margin:0 auto;padding:0 0 34px;color:var(--ink)}
.nk-home-v4-head{display:flex;align-items:flex-end;justify-content:space-between;gap:24px;padding:24px 4px 20px;border-bottom:1px solid #e2e4eb}
.nk-home-v4-kicker,.nk-home-v4-label{font-size:10px;font-weight:850;letter-spacing:1.55px;text-transform:uppercase;color:#536aa5}
.nk-home-v4-head h1{font-size:32px;line-height:1.05;letter-spacing:-1.5px;margin:6px 0 5px;font-weight:850}
.nk-home-v4-head p{margin:0;color:#70727f;font-size:14px}
.nk-home-v4-continue{border:1px solid #d9dce6;background:#fff;color:#2f2d63;min-height:44px;padding:0 17px;border-radius:12px;font-weight:800;font-size:13px;white-space:nowrap}
.nk-home-v4-continue span{margin-left:8px;font-size:16px}
.nk-home-v4-today{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:28px;align-items:end;padding:26px 22px 24px;background:linear-gradient(112deg,#302d63 0%,#3d59b6 62%,#4d6bd3 100%);color:#fff;position:relative;overflow:hidden}
.nk-home-v4-today:after{content:"";position:absolute;width:280px;height:280px;border-radius:50%;right:-130px;top:-150px;border:1px solid rgba(255,255,255,.12);box-shadow:0 0 0 40px rgba(255,255,255,.025),0 0 0 80px rgba(255,255,255,.018)}
.nk-home-v4-today-copy,.nk-home-v4-actions{position:relative;z-index:1}
.nk-home-v4-today .nk-home-v4-label{color:rgba(255,255,255,.7)}
.nk-home-v4-today h2{font-size:23px;line-height:1.16;letter-spacing:-.55px;margin:6px 0 6px;max-width:690px}
.nk-home-v4-today p{font-size:13px;line-height:1.4;color:rgba(255,255,255,.78);margin:0;max-width:640px}
.nk-home-v4-actions{display:flex;gap:8px;align-items:center}
.nk-home-v4-primary,.nk-home-v4-secondary{min-height:44px;border-radius:11px;padding:0 15px;font-size:13px;font-weight:800;white-space:nowrap}
.nk-home-v4-primary{border:0;background:#fff;color:#2f2d63}.nk-home-v4-secondary{border:1px solid rgba(255,255,255,.28);background:rgba(255,255,255,.08);color:#fff}.nk-home-v4-primary span,.nk-home-v4-secondary span{margin-left:8px}
.nk-home-v4-section{padding-top:28px}
.nk-home-v4-section-head{display:flex;align-items:end;justify-content:space-between;gap:16px;padding:0 4px 11px}
.nk-home-v4-section-head h2{font-size:22px;letter-spacing:-.7px;line-height:1.05;margin:4px 0 0;font-weight:850}
.nk-home-v4-section-head>span{font-size:12px;color:#777986}
.nk-home-v4-link{border:0;background:none;color:#536aa5;font-size:12px;font-weight:800;padding:3px 0}
.nk-home-v4-subject-list{border-top:1px solid #dfe2ea;border-bottom:1px solid #dfe2ea}
.nk-home-v4-subject{display:grid;grid-template-columns:38px minmax(0,1fr) 42px 24px;gap:12px;align-items:center;width:100%;min-height:88px;padding:12px 10px 12px 4px;border:0;border-bottom:1px solid #e6e8ee;background:transparent;text-align:left;color:var(--ink);cursor:pointer}
.nk-home-v4-subject:last-child{border-bottom:0}.nk-home-v4-subject:hover{background:#f7f8fb}.nk-home-v4-subject.is-active{background:#f5f5fb;box-shadow:inset 3px 0 0 #3d65d8}
.nk-home-v4-subject-index{font-size:11px;color:#9699a5;font-weight:800;text-align:center}
.nk-home-v4-subject-main{display:grid;grid-template-columns:minmax(0,1fr);gap:3px}.nk-home-v4-subject-main strong{font-size:15px;font-weight:800}.nk-home-v4-subject-main small{font-size:11px;color:#858793}.nk-home-v4-progress{display:block;height:4px;background:#eceef3;border-radius:99px;overflow:hidden;margin-top:4px;max-width:320px}.nk-home-v4-progress i{display:block;height:100%;background:#536aa5;border-radius:99px}
.nk-home-v4-subject-pct{font-size:12px;font-weight:800;color:#666976;text-align:right}.nk-home-v4-chevron{font-size:18px;color:#a0a2ab;text-align:right}
.nk-home-v4-metrics{display:grid;grid-template-columns:repeat(4,1fr);border-top:1px solid #dfe2ea;border-bottom:1px solid #dfe2ea}
.nk-home-v4-metrics>div{padding:16px 18px 15px;border-right:1px solid #e4e6ec}.nk-home-v4-metrics>div:last-child{border-right:0}.nk-home-v4-metrics b{display:block;font-size:24px;letter-spacing:-.7px}.nk-home-v4-metrics span{display:block;font-size:12px;font-weight:800;margin-top:2px}.nk-home-v4-metrics small{display:block;font-size:10px;color:#898b96;margin-top:2px}
.nk-home-v4-tool-grid{display:grid;grid-template-columns:repeat(4,1fr);border-top:1px solid #dfe2ea;border-bottom:1px solid #dfe2ea}
.nk-home-v4-tool-grid button{position:relative;min-height:76px;padding:13px 34px 13px 14px;border:0;border-right:1px solid #e4e6ec;background:#fff;text-align:left;color:var(--ink)}.nk-home-v4-tool-grid button:last-child{border-right:0}.nk-home-v4-tool-grid button:hover{background:#f7f8fb}.nk-home-v4-tool-grid span{display:block;font-size:13px;font-weight:800}.nk-home-v4-tool-grid small{display:block;color:#858793;font-size:10px;margin-top:4px}.nk-home-v4-tool-grid b{position:absolute;right:12px;top:50%;transform:translateY(-50%);font-size:16px;color:#9b9da7}
.nk-home-v4-two-col{display:grid;grid-template-columns:1.15fr .85fr;gap:34px}.nk-home-v4-chapter{display:grid;grid-template-columns:24px minmax(0,1fr) 48px;gap:10px;align-items:center;min-height:58px;border-bottom:1px solid #e8e9ee}.nk-home-v4-chapter>span{font-size:11px;color:#999ba5;font-weight:800}.nk-home-v4-chapter strong{display:block;font-size:12px}.nk-home-v4-chapter small{display:block;font-size:10px;color:#858793;margin-top:2px}.nk-home-v4-chapter>b{font-size:12px;text-align:right}.nk-home-v4-empty{font-size:12px;color:#858793;padding:14px 0;border-bottom:1px solid #e8e9ee}
.nk-home-v4-lower .recent-row{border-bottom:1px solid #e8e9ee;border-radius:0!important;min-height:54px}
@media(max-width:760px){.nk-home-v4{padding-bottom:24px}.nk-home-v4-head{padding:20px 0 16px}.nk-home-v4-head h1{font-size:28px}.nk-home-v4-today{grid-template-columns:1fr;gap:16px;padding:22px 18px}.nk-home-v4-actions{flex-wrap:wrap}.nk-home-v4-two-col{grid-template-columns:1fr;gap:28px}}
@media(max-width:560px){.nk-home-v4-head{align-items:flex-start;gap:12px}.nk-home-v4-head h1{font-size:27px}.nk-home-v4-head p{font-size:12px}.nk-home-v4-continue{min-height:40px;padding:0 12px}.nk-home-v4-today h2{font-size:20px}.nk-home-v4-section{padding-top:24px}.nk-home-v4-section-head h2{font-size:21px}.nk-home-v4-subject{grid-template-columns:28px minmax(0,1fr) 38px 18px;gap:9px;min-height:84px;padding-right:4px}.nk-home-v4-subject-main small{font-size:10px}.nk-home-v4-metrics{grid-template-columns:repeat(2,1fr)}.nk-home-v4-metrics>div:nth-child(2){border-right:0}.nk-home-v4-metrics>div:nth-child(-n+2){border-bottom:1px solid #e4e6ec}.nk-home-v4-tool-grid{grid-template-columns:repeat(2,1fr)}.nk-home-v4-tool-grid button:nth-child(2){border-right:0}.nk-home-v4-tool-grid button:nth-child(-n+2){border-bottom:1px solid #e4e6ec}.nk-home-v4-tool-grid button{min-height:70px}.nk-home-v4-two-col{gap:24px}}
</style>
'''

s=INDEX.read_text(encoding='utf-8')
start=s.index('function dashboard() {')
end=s.index('  function testRow(t) {', start)
s=s[:start]+DASHBOARD+s[end:]
# Remove any previous V4 style marker so the transformation is idempotent.
s=re.sub(r'<style id="nk-home-v4-style">.*?</style>\s*', '', s, flags=re.S)
pos=s.rfind('</head>')
if pos==-1: raise SystemExit('No </head> in index.html')
s=s[:pos]+CSS+'\n'+s[pos:]
INDEX.write_text(s,encoding='utf-8')

# Runtime injection was the reason the earlier visual changes did not reliably
# reach the device. Keep MainActivity focused on the WebView/PDF plumbing.
m=MAIN.read_text(encoding='utf-8')
m=m.replace('                injectHomePolish();\n','')
m=re.sub(r'\n    private void injectHomePolish\(\) \{.*?\n    \}\n', '\n', m, flags=re.S)
MAIN.write_text(m,encoding='utf-8')

print('Applied NK Home V4 directly to generated index.html and disabled runtime Home injection.')
