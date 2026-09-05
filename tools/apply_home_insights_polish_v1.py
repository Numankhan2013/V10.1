from pathlib import Path
import re

HTML = Path('app/src/main/assets/index.html')
s = HTML.read_text(encoding='utf-8')
s = re.sub(r'<style id="qbank-home-insights-polish-v1">.*?</style>\s*', '', s, flags=re.S)

needle = '  function subjectPickerMarkup(){'
if needle not in s:
    raise SystemExit('subjectPickerMarkup not found')
subject_icon = r'''  function subjectIcon(name, size=46){
    const n=String(name||'').toLowerCase();
    if(n==='anatomy') return `<svg class="subject-svg anatomy" width="${size}" height="${size}" viewBox="0 0 48 48" aria-hidden="true"><path d="M17 9c-3 0-5 2-5 5v7c0 2 1 4 3 5l-2 10c0 2 2 4 4 4h2l2-9h2l2 9h2c2 0 4-2 4-4l-2-10c2-1 3-3 3-5v-7c0-3-2-5-5-5h-8Z" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linejoin="round"/><path d="M12 20h24M17 26h14M19 9v7m10-7v7" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>`;
    if(n==='physiology') return `<svg class="subject-svg physiology" width="${size}" height="${size}" viewBox="0 0 48 48" aria-hidden="true"><circle cx="24" cy="9" r="4" fill="none" stroke="currentColor" stroke-width="2.2"/><path d="M24 13v13m0-9-9-3m9 3 9-3M24 26l-8 12m8-12 8 12M15 21l-5 7m23-7 5 7" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/><path d="M19 19h10" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"/></svg>`;
    return `<svg class="subject-svg biochemistry" width="${size}" height="${size}" viewBox="0 0 48 48" aria-hidden="true"><path d="M18 5v8l-8 23a5 5 0 0 0 5 7h18a5 5 0 0 0 5-7l-8-23V5" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/><path d="M16 25h16M14 34c5-3 10 4 19 0" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/><path d="M23 10h8" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"/></svg>`;
  }

'''
s = s.replace(needle, subject_icon + needle, 1)
old_mark = '<span class="v102-subject-mark">${esc(x.subject.slice(0,2).toUpperCase())}</span>'
new_mark = '<span class="v102-subject-mark">${subjectIcon(x.subject,46)}</span>'
if old_mark not in s:
    raise SystemExit('Subject initials markup not found')
s = s.replace(old_mark, new_mark, 1)

streak_start = s.find('  function streakMarkup() {')
streak_end = s.find('\n  function flameIcon', streak_start)
if streak_start < 0 or streak_end < 0:
    raise SystemExit('streakMarkup boundaries not found')
new_streak = r'''  function streakMarkup(){
    const streak=currentStreak();
    const days=new Set();
    for(const a of Object.values(state.attempts)) for(const x of a) if(x.ts) days.add(dayKey(new Date(x.ts)));
    const now=new Date(), dayNames=['S','M','T','W','T','F','S'], items=[];
    for(let i=6;i>=0;i--){ const d=new Date(now); d.setDate(d.getDate()-i); const key=dayKey(d), active=days.has(key), isToday=i===0; items.push(`<div class="streak-mini-day ${active?'done':''} ${isToday?'today':''}"><span>${active?'✓':dayNames[d.getDay()]}</span></div>`); }
    return `<section class="card streak-card streak-card-compact"><div class="streak-compact-main"><div class="streak-compact-flame">${flameIcon(28)}</div><div><div class="streak-compact-title">Study streak</div><div class="streak-compact-number">${streak}<span> day${streak===1?'':'s'}</span></div></div></div><div class="streak-compact-week">${items.join('')}</div><div class="streak-compact-note">${streak?'Keep the chain alive today.':'Start today to begin your streak.'}</div></section>`;
  }
'''
s = s[:streak_start] + new_streak + s[streak_end:]

old_order = '''      <div class="dashboard-v10">
        ${subjectPickerMarkup()}
        <div class="dashboard-greeting">'''
new_order = '''      <div class="dashboard-v10">
        <div class="dashboard-greeting">'''
if old_order not in s:
    raise SystemExit('Dashboard subject-first order not found')
s = s.replace(old_order, new_order, 1)
old_after_focus = '''        </section>
        ${streakMarkup()}<div class="dashboard-section">'''
new_after_focus = '''        </section>
        ${streakMarkup()}
        ${subjectPickerMarkup()}
        <div class="dashboard-section">'''
if old_after_focus not in s:
    raise SystemExit('Dashboard streak insertion point not found')
s = s.replace(old_after_focus, new_after_focus, 1)

old_analytics = '''      <div class="grid grid-4"><div class="card stat-card"><div class="label">Accuracy</div><div class="value">${fmtPct(overallAccuracy())}</div><div class="small-muted">${fmtNum(totalAttempts())} attempts</div></div><div class="card stat-card"><div class="label">Avg. time / question</div><div class="value">${formatDuration(avgTime)}</div><div class="small-muted">Practice attempts</div></div><div class="card stat-card"><div class="label">Questions due</div><div class="value">${fmtNum(pendingReviewCount())}</div><div class="small-muted">Spaced review</div></div><div class="card stat-card"><div class="label">Study time</div><div class="value">${formatDuration(totalStudyMs())}</div><div class="small-muted">Local history</div></div></div>'''
new_analytics = '''      <div class="insight-stat-grid">
        <div class="card stat-card insight-stat insight-accuracy"><div class="insight-stat-head"><span class="insight-icon">${navIcon('check',18)}</span><span class="label">Accuracy</span></div><div class="value">${fmtPct(overallAccuracy())}</div><div class="small-muted">${fmtNum(totalAttempts())} attempts</div></div>
        <div class="card stat-card insight-stat insight-time"><div class="insight-stat-head"><span class="insight-icon">${navIcon('clock',18)}</span><span class="label">Avg. time / question</span></div><div class="value">${formatDuration(avgTime)}</div><div class="small-muted">Practice attempts</div></div>
        <div class="card stat-card insight-stat insight-due"><div class="insight-stat-head"><span class="insight-icon">${navIcon('refresh',18)}</span><span class="label">Questions due</span></div><div class="value">${fmtNum(pendingReviewCount())}</div><div class="small-muted">Spaced review</div></div>
        <div class="card stat-card insight-stat insight-study"><div class="insight-stat-head"><span class="insight-icon">${navIcon('chart',18)}</span><span class="label">Study time</span></div><div class="value">${formatDuration(totalStudyMs())}</div><div class="small-muted">Local history</div></div>
      </div>'''
if old_analytics not in s:
    raise SystemExit('Analytics stat grid not found')
s = s.replace(old_analytics, new_analytics, 1)

css = r'''<style id="qbank-home-insights-polish-v1">
.v102-subject-mark { display:grid !important; place-items:center !important; }
.v102-subject-mark .subject-svg { width:44px; height:44px; }
.v102-subject-card:nth-child(1) .v102-subject-mark { color:#a33a80; background:#f3e5f1 !important; }
.v102-subject-card:nth-child(2) .v102-subject-mark { color:#8a6a35; background:#f4ecdd !important; }
.v102-subject-card:nth-child(3) .v102-subject-mark { color:#3272b5; background:#e5f0fb !important; }
.dashboard-v10 > .v102-subject-hub { margin-top:14px; }
.streak-card-compact { padding:12px 14px !important; border-radius:17px !important; }
.streak-compact-main { display:flex; align-items:center; gap:10px; }
.streak-compact-flame { width:38px; height:38px; display:grid; place-items:center; border-radius:12px; background:#fff4d9; border:1px solid #f1dfb4; }
.streak-compact-flame .flame-svg { width:27px; height:27px; }
.streak-compact-title { font-size:12px; font-weight:800; }
.streak-compact-number { margin-top:1px; font-size:21px; line-height:1.05; font-weight:880; letter-spacing:-.3px; }
.streak-compact-number span { font-size:11px; color:var(--muted); font-weight:650; }
.streak-compact-week { display:flex; gap:6px; margin-left:48px; margin-top:-2px; }
.streak-mini-day { width:22px; height:22px; border-radius:50%; display:grid; place-items:center; background:#f0f1f5; color:#999baa; font-size:8px; font-weight:800; }
.streak-mini-day.done { background:#fff0c9; color:#c98216; }
.streak-mini-day.today { box-shadow:0 0 0 2px rgba(61,101,216,.13); }
.streak-compact-note { margin:6px 0 0 48px; font-size:9.5px; color:var(--muted); }
.insight-stat-grid { display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:14px; }
.insight-stat { min-height:112px !important; padding:14px !important; }
.insight-stat-head { display:flex; align-items:center; gap:9px; min-height:28px; }
.insight-stat-head .label { margin:0; font-size:12px !important; font-weight:750 !important; color:#6f7180 !important; }
.insight-icon { width:31px; height:31px; border-radius:10px; display:grid; place-items:center; flex:none; }
.insight-icon svg { width:18px; height:18px; }
.insight-stat .value { margin-top:9px; }
.insight-accuracy .insight-icon { background:#eaf8f3; color:#159a74; }
.insight-time .insight-icon { background:#eef0fa; color:#3d65d8; }
.insight-due .insight-icon { background:#fff4df; color:#bd7c18; }
.insight-study .insight-icon { background:#f3f0fb; color:#6c55a8; }
@media(max-width:900px){ .insight-stat-grid { grid-template-columns:1fr 1fr; } }
@media(max-width:640px){
  .streak-card-compact { padding:11px 12px !important; }
  .streak-compact-week { margin-left:47px; gap:5px; }
  .streak-mini-day { width:21px; height:21px; }
  .insight-stat-grid { gap:10px; }
  .insight-stat { min-height:106px !important; padding:12px !important; }
  .insight-stat-head .label { font-size:10.5px !important; }
  .insight-stat .value { font-size:21px !important; }
}
@media(max-width:390px){
  .streak-compact-week { margin-left:0; margin-top:8px; }
  .streak-compact-note { margin-left:0; }
}
</style>'''
if '</head>' not in s:
    raise SystemExit('</head> missing')
s = s.replace('</head>', css+'\n</head>', 1)
HTML.write_text(s, encoding='utf-8')
print('V10.3.8 home + insights polish applied.')
