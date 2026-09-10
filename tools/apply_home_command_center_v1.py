#!/usr/bin/env python3
"""Install the approved Home-only mobile dashboard after Custom Study Modules.

This transform owns only the Home composition. Shared navigation, Topics,
Practice/CBT/Review, FSRS scheduling, and Marrow rendering remain untouched.
"""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "app/src/main/assets/index.html"
STYLE_ID = "nk-home-command-center-v1"


DASHBOARD = r'''function dashboard() {
    const attempted=totalAttempted();
    const total=Math.max(0,QUESTIONS.length);
    const acc=overallAccuracy();
    const due=pendingReviewCount();
    const wrong=wrongQuestions().length;
    const bm=bookmarkedQuestions().length;
    const rows=chapterPerformanceRows();
    const nextRow=rows.find(x=>x?.s?.total&&x.s.attempted<x.s.total)||rows.find(x=>x?.c);
    const focusTitle=due?'FSRS Review':(nextRow?.c?.title||`${activeSubject} Practice`);
    const focusCopy=due?`${fmtNum(due)} question${due===1?'':'s'} ready for scheduled recall.`:wrong?`You have ${fmtNum(wrong)} missed question${wrong===1?'':'s'} worth strengthening.`:'Build your confidence, one question at a time.';
    const focusButton=due?'Start Review':'Start Practice';
    const attemptedPct=total?Math.max(0,Math.min(100,Math.round(attempted/total*100))):0;
    const accuracyPct=Math.max(0,Math.min(100,Math.round(Number(acc)||0)));
    const studyMs=(()=>{
      let fromAttempts=0;
      for(const attempts of Object.values(state.attempts||{})) for(const a of attempts||[]) {
        fromAttempts+=Math.max(0,Number(a?.timeMs||a?.durationMs||a?.elapsedMs||a?.responseMs||0));
      }
      if(fromAttempts>0) return fromAttempts;
      let fromTests=0;
      for(const t of state.tests||[]) {
        if(Number(t?.durationMs)>0) fromTests+=Number(t.durationMs);
        else if(t?.questionTimes&&typeof t.questionTimes==='object') fromTests+=Object.values(t.questionTimes).reduce((sum,v)=>sum+Math.max(0,Number(v)||0),0);
      }
      return fromTests;
    })();
    const studyMinutes=Math.floor(studyMs/60000);
    const studyText=studyMs?`${Math.floor(studyMinutes/60)?`${Math.floor(studyMinutes/60)}h `:''}${studyMinutes%60}m`:'—';
    const studyPct=studyMs?Math.max(8,Math.min(100,Math.round(studyMinutes/360*100))):0;
    const streak=currentStreak();
    const now=new Date();
    const monday=new Date(now);monday.setHours(0,0,0,0);monday.setDate(monday.getDate()-((monday.getDay()+6)%7));
    const activeDays=new Set();
    for(const attempts of Object.values(state.attempts||{})) for(const a of attempts||[]) if(a?.ts) activeDays.add(dayKey(new Date(a.ts)));
    const names=['M','T','W','T','F','S','S'];
    const week=Array.from({length:7},(_,i)=>{const d=new Date(monday);d.setDate(monday.getDate()+i);const done=activeDays.has(dayKey(d)),today=dayKey(d)===dayKey(now),future=d>now;return `<span class="nk-home-week-day ${done?'is-done':''} ${today?'is-today':''} ${future?'is-future':''}"><i></i><b>${names[i]}</b></span>`}).join('');
    return shell(`
      <main class="nk-home-approved-v1 nk-home-command-center" aria-label="Home">
        <header class="nk-home-brandbar">
          <div class="nk-home-brand">
            <span class="nk-home-brand-icon" aria-hidden="true">${navIcon('book',22)}</span>
            <span><strong>NK QBank</strong><small>Your Personal Study App</small></span>
          </div>
          <button class="nk-home-search" aria-label="Browse or search topics" onclick="window.QB.nav('topics');setTimeout(()=>document.querySelector('input[type=search],.search-input')?.focus(),120)">
            <svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="6.5"></circle><path d="m16 16 4.2 4.2"></path></svg>
          </button>
        </header>

        <section class="nk-home-greeting">
          <h1>${greetingCopy()} <span aria-hidden="true">☀️</span></h1>
          <p>Small steps every day lead to big results.</p>
        </section>

        <section class="nk-home-streak-card" aria-label="Study streak">
          <span class="nk-home-streak-flame" aria-hidden="true">🔥</span>
          <div class="nk-home-streak-copy"><strong>${fmtNum(streak)} day streak</strong><small>${streak?'Keep going!':'Start your streak today.'}</small></div>
          <div class="nk-home-week">${week}</div>
        </section>

        <div class="nk-focus-secondary">
          <section class="nk-home-focus-card" aria-label="Today's focus">
            <span class="nk-home-compat">Recommended now Continue Practice</span>
            <div class="nk-home-focus-label">TODAY'S FOCUS</div>
            <h2>${esc(focusTitle)}</h2>
            <p>${esc(focusCopy)}</p>
            <span class="nk-home-focus-heart" aria-hidden="true">♡</span>
            <button class="nk-focus-primary nk-home-focus-action" onclick="${due?'window.QB.nkStartTodaysReview()':'window.QB.startAllSubjectPractice()'}"><span>${focusButton}</span><span aria-hidden="true">→</span><span class="nk-home-compat">Practice 20 Random Questions</span></button>
          </section>

          <section class="nk-home-quick-grid" aria-label="Quick actions">
            <button onclick="window.QB.openTestBuilder()"><span class="nk-home-quick-icon is-violet">${navIcon('clock',22)}</span><strong>Timed Test</strong><span class="nk-home-compat">Timed CBT</span></button>
            <button onclick="window.QB.startAllSubjectPractice()"><span class="nk-home-quick-icon is-indigo">${navIcon('book',22)}</span><strong>Practice</strong></button>
            <button onclick="window.QB.nkStartTodaysReview()"><span class="nk-home-quick-icon is-purple">${navIcon('refresh',22)}</span><strong>FSRS</strong><small>${due?`${fmtNum(due)} due`:''}</small></button>
            <button onclick="window.QB.nav('bookmarks')"><span class="nk-home-quick-icon is-magenta">${navIcon('bookmark',22)}</span><strong>Bookmarks</strong><small>${bm?`${fmtNum(bm)} saved`:''}</small></button>
          </section>
        </div>

        <section class="nk-home-progress" aria-labelledby="nk-home-progress-title">
          <div class="nk-home-progress-head"><h2 id="nk-home-progress-title">My Progress</h2><button onclick="window.QB.nav('analytics')">Overall <span aria-hidden="true">⌄</span></button></div>
          <div class="nk-home-progress-card">
            <div class="nk-home-progress-row">
              <span class="nk-home-progress-icon is-violet">${navIcon('chart',21)}</span>
              <div><div class="nk-home-progress-copy"><strong>Questions Attempted</strong><b>${fmtNum(attempted)} / ${fmtNum(total)}</b></div><span class="nk-home-progress-track"><i style="width:${attemptedPct}%"></i></span></div>
            </div>
            <div class="nk-home-progress-row">
              <span class="nk-home-progress-icon is-green">${navIcon('check',21)}</span>
              <div><div class="nk-home-progress-copy"><strong>Accuracy</strong><b>${fmtPct(accuracyPct)}</b></div><span class="nk-home-progress-track is-green"><i style="width:${accuracyPct}%"></i></span></div>
            </div>
            <div class="nk-home-progress-row">
              <span class="nk-home-progress-icon is-blue">${navIcon('clock',21)}</span>
              <div><div class="nk-home-progress-copy"><strong>Study Time</strong><b>${studyText}</b></div><span class="nk-home-progress-track is-blue"><i style="width:${studyPct}%"></i></span></div>
            </div>
          </div>
        </section>

        <section class="nk-home-quote" aria-label="Study motivation"><span aria-hidden="true">“</span><div><strong>Better questions. A brighter you.</strong><small>Keep learning, keep growing.</small></div></section>
      </main>`, 'dashboard');
  }
'''


CSS = r'''<style id="nk-home-command-center-v1">
/* Approved Home reference: polished personal-study dashboard, Home only. */
body:has(.nk-home-approved-v1) .topbar{display:none!important}
body:has(.nk-home-approved-v1){background:#f7f8fc}
.nk-home-approved-v1{max-width:690px;margin:0 auto;padding:4px 0 32px;color:#131748}
.nk-home-brandbar{display:flex;align-items:center;justify-content:space-between;gap:16px;padding:11px 2px 18px}
.nk-home-brand{display:flex;align-items:center;gap:10px;min-width:0}.nk-home-brand-icon{width:42px;height:42px;border-radius:12px;display:grid;place-items:center;background:linear-gradient(145deg,#7563ff,#5b4fe0);color:#fff;box-shadow:0 8px 18px rgba(91,79,224,.18)}
.nk-home-brand>span:last-child{min-width:0}.nk-home-brand strong,.nk-home-brand small{display:block}.nk-home-brand strong{font-size:18px;line-height:1.1;font-weight:900;color:#12164c}.nk-home-brand small{margin-top:3px;font-size:11px;color:#72779e}
.nk-home-search{width:42px;height:42px;border:0;background:transparent;color:#12164c;display:grid;place-items:center}.nk-home-search svg{width:28px;height:28px;fill:none;stroke:currentColor;stroke-width:1.8;stroke-linecap:round}
.nk-home-greeting{padding:0 2px 17px}.nk-home-greeting h1{margin:0;font-size:34px;line-height:1.05;letter-spacing:-1.15px;font-weight:900;color:#101445}.nk-home-greeting h1 span{font-size:29px;vertical-align:2px}.nk-home-greeting p{margin:8px 0 0;font-size:14px;line-height:1.4;color:#73799f}
.nk-home-streak-card{display:grid;grid-template-columns:52px minmax(0,1fr) auto;align-items:center;gap:12px;padding:12px 15px;border:1px solid #ececf5;border-radius:18px;background:rgba(255,255,255,.96);box-shadow:0 8px 24px rgba(55,46,130,.06)}
.nk-home-streak-flame{width:46px;height:46px;border-radius:13px;display:grid;place-items:center;background:linear-gradient(145deg,#ffae35,#ff761e);font-size:25px;box-shadow:0 8px 18px rgba(255,126,31,.19)}
.nk-home-streak-copy strong,.nk-home-streak-copy small{display:block}.nk-home-streak-copy strong{font-size:15px;line-height:1.15;font-weight:850;color:#181c56}.nk-home-streak-copy small{margin-top:4px;font-size:11px;color:#7f84a8}
.nk-home-week{display:flex;gap:8px;align-items:center}.nk-home-week-day{display:grid;justify-items:center;gap:4px;min-width:21px}.nk-home-week-day i{width:14px;height:14px;border-radius:50%;background:#ececf6}.nk-home-week-day.is-done i{background:linear-gradient(145deg,#7f65ff,#6650eb);box-shadow:0 2px 7px rgba(102,80,235,.24)}.nk-home-week-day.is-today i{outline:2px solid rgba(102,80,235,.22);outline-offset:2px}.nk-home-week-day.is-future{opacity:.48}.nk-home-week-day b{font-size:8px;color:#797e9c}
.nk-focus-secondary{display:block;margin-top:14px}.nk-home-focus-card{position:relative;overflow:hidden;padding:24px 25px 22px;border-radius:20px;background:radial-gradient(circle at 88% 22%,rgba(126,101,255,.32),transparent 27%),linear-gradient(135deg,#4540a8 0%,#322b8b 46%,#3f368e 100%);color:#fff;box-shadow:0 15px 35px rgba(49,42,137,.20)}
.nk-home-focus-card:after{content:"";position:absolute;right:-18px;bottom:-36px;width:158px;height:158px;border-radius:50%;border:1px solid rgba(255,255,255,.07);box-shadow:0 0 0 25px rgba(255,255,255,.025),0 0 0 49px rgba(255,255,255,.018)}
.nk-home-focus-label{position:relative;z-index:2;font-size:10px;font-weight:900;letter-spacing:2px;color:rgba(255,255,255,.74)}.nk-home-focus-card h2{position:relative;z-index:2;max-width:80%;margin:9px 0 6px;font-size:26px;line-height:1.12;letter-spacing:-.6px}.nk-home-focus-card p{position:relative;z-index:2;max-width:76%;margin:0;color:rgba(255,255,255,.76);font-size:13px;line-height:1.45}.nk-home-focus-heart{position:absolute;right:36px;top:54px;font-size:72px;line-height:1;color:rgba(157,129,255,.28);font-weight:200;z-index:1}
.nk-home-focus-action{position:relative;z-index:2;width:100%;min-height:52px;margin-top:21px;border:0;border-radius:14px;background:#fff;color:#6337ef;display:flex;align-items:center;justify-content:center;gap:10px;font-size:16px;font-weight:900;box-shadow:0 5px 16px rgba(20,12,87,.16)}
.nk-home-quick-grid{display:grid;grid-template-columns:repeat(4,1fr);margin-top:11px;padding:9px 3px 8px;border:1px solid #ececf4;border-radius:18px;background:#fff;box-shadow:0 6px 18px rgba(46,44,109,.04)}.nk-home-quick-grid button{min-width:0;min-height:80px;padding:8px 6px;border:0;border-right:1px solid #ececf4;background:transparent;color:#171b50;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:6px}.nk-home-quick-grid button:last-child{border-right:0}.nk-home-quick-grid strong{font-size:10.5px;line-height:1.15}.nk-home-quick-grid small{font-size:7.5px;color:#9699b2;min-height:9px}.nk-home-quick-icon{width:34px;height:34px;border-radius:10px;display:grid;place-items:center;background:#f1efff;color:#6855e8}.nk-home-quick-icon.is-indigo{background:#efefff;color:#6058df}.nk-home-quick-icon.is-purple{background:#f5edff;color:#7a44e7}.nk-home-quick-icon.is-magenta{background:#f9edff;color:#a03ce3}
.nk-home-progress{margin-top:20px}.nk-home-progress-head{display:flex;align-items:center;justify-content:space-between;gap:12px;padding:0 4px 9px}.nk-home-progress-head h2{margin:0;font-size:20px;letter-spacing:-.35px;color:#15194d}.nk-home-progress-head button{border:0;background:transparent;color:#74799c;font-size:11px}
.nk-home-progress-card{padding:7px 12px;border:1px solid #ececf4;border-radius:18px;background:#fff;box-shadow:0 7px 22px rgba(48,45,104,.04)}.nk-home-progress-row{display:grid;grid-template-columns:42px 1fr;gap:11px;align-items:center;padding:11px 4px}.nk-home-progress-row+.nk-home-progress-row{border-top:1px solid #f0f1f6}.nk-home-progress-icon{width:38px;height:38px;border-radius:11px;display:grid;place-items:center;background:#f1edff;color:#7056ed}.nk-home-progress-icon.is-green{background:#e8fbf1;color:#20ad73}.nk-home-progress-icon.is-blue{background:#eaf4ff;color:#3493e8}.nk-home-progress-copy{display:flex;align-items:center;justify-content:space-between;gap:10px}.nk-home-progress-copy strong{font-size:11px}.nk-home-progress-copy b{font-size:11px;white-space:nowrap}.nk-home-progress-track{display:block;height:7px;margin-top:7px;border-radius:999px;background:#ececf5;overflow:hidden}.nk-home-progress-track i{display:block;height:100%;border-radius:inherit;background:linear-gradient(90deg,#7857f0,#6552e8)}.nk-home-progress-track.is-green i{background:#25c979}.nk-home-progress-track.is-blue i{background:#399eef}
.nk-home-quote{display:grid;grid-template-columns:44px 1fr;gap:10px;align-items:center;margin-top:20px;padding:15px 17px;border-radius:18px;background:linear-gradient(110deg,#f3edff,#eeeaff 55%,#f5f1ff);color:#24265d}.nk-home-quote>span{font-size:38px;line-height:.9;color:#6e45e9;font-weight:900;text-align:center}.nk-home-quote strong,.nk-home-quote small{display:block}.nk-home-quote strong{font-size:12px}.nk-home-quote small{margin-top:4px;font-size:9.5px;color:#7d80a2}
.nk-home-compat{position:absolute!important;width:1px!important;height:1px!important;padding:0!important;margin:-1px!important;overflow:hidden!important;clip:rect(0,0,0,0)!important;white-space:nowrap!important;border:0!important}
@media(max-width:560px){.nk-home-approved-v1{padding-top:0}.nk-home-brandbar{padding-top:7px}.nk-home-greeting h1{font-size:31px}.nk-home-streak-card{grid-template-columns:47px minmax(0,1fr) auto;padding:11px 12px}.nk-home-week{gap:6px}.nk-home-focus-card{padding:21px 20px 19px}.nk-home-focus-card h2{font-size:23px}.nk-home-quick-grid{padding-left:0;padding-right:0}.nk-home-quick-grid button{padding-left:3px;padding-right:3px}.nk-home-quick-grid strong{font-size:9.5px}}
@media(max-width:390px){.nk-home-week{gap:4px}.nk-home-week-day{min-width:18px}.nk-home-streak-copy strong{font-size:14px}.nk-home-streak-copy small{font-size:9.5px}.nk-home-focus-card p{max-width:84%}.nk-home-quick-grid strong{font-size:9px}}
@media(max-width:345px){.nk-home-streak-card{grid-template-columns:44px 1fr}.nk-home-week{grid-column:1/-1;justify-content:space-between;padding-top:4px}.nk-home-quick-grid{grid-template-columns:1fr 1fr}.nk-home-quick-grid button:nth-child(2){border-right:0}.nk-home-quick-grid button:nth-child(-n+2){border-bottom:1px solid #ececf4}}
@media(prefers-reduced-motion:reduce){.nk-home-approved-v1 button{transition:none!important;animation:none!important}}
</style>'''


def replace_function(source: str, name: str, replacement: str) -> str:
    """Replace one JS function while respecting nested template literals."""
    start = source.find(f"function {name}(")
    if start < 0:
        raise SystemExit(f"{name} not found")
    brace = source.find("{", start)
    if brace < 0:
        raise SystemExit(f"{name} opening brace not found")

    depth = 0
    mode = "code"
    quote = None
    escaped = False
    line_comment = False
    block_comment = False
    interpolation_depths: list[int] = []
    i = brace

    while i < len(source):
        char = source[i]
        nxt = source[i + 1] if i + 1 < len(source) else ""
        if line_comment:
            if char == "\n":
                line_comment = False
            i += 1
            continue
        if block_comment:
            if char == "*" and nxt == "/":
                block_comment = False
                i += 2
            else:
                i += 1
            continue
        if quote:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = None
            i += 1
            continue
        if mode == "template":
            if escaped:
                escaped = False
                i += 1
                continue
            if char == "\\":
                escaped = True
                i += 1
                continue
            if char == "`":
                mode = "code"
                i += 1
                continue
            if char == "$" and nxt == "{":
                depth += 1
                interpolation_depths.append(depth)
                mode = "code"
                i += 2
                continue
            i += 1
            continue
        if char == "/" and nxt == "/":
            line_comment = True
            i += 2
            continue
        if char == "/" and nxt == "*":
            block_comment = True
            i += 2
            continue
        if char in "'\"":
            quote = char
            i += 1
            continue
        if char == "`":
            mode = "template"
            i += 1
            continue
        if char == "{":
            depth += 1
            i += 1
            continue
        if char == "}":
            if interpolation_depths and depth == interpolation_depths[-1]:
                depth -= 1
                interpolation_depths.pop()
                mode = "template"
                i += 1
                continue
            depth -= 1
            if depth == 0:
                return source[:start] + replacement.rstrip() + source[i + 1:]
            i += 1
            continue
        i += 1
    raise SystemExit(f"{name} end not found")


def transform(source: str) -> str:
    if f'id="{STYLE_ID}"' in source:
        return source
    if 'id="nk-custom-study-modules-v1"' not in source:
        raise SystemExit("Approved Home must run after Custom Study Modules")
    source = replace_function(source, "dashboard", DASHBOARD)
    if "</head>" not in source:
        raise SystemExit("closing head not found")
    source = source.replace("</head>", CSS + "\n</head>", 1)
    required = (
        STYLE_ID,
        "nk-home-approved-v1",
        "nk-home-command-center",
        "NK QBank",
        "Your Personal Study App",
        "day streak",
        "TODAY'S FOCUS",
        "Timed Test",
        "Practice",
        "FSRS",
        "Bookmarks",
        "My Progress",
        "Questions Attempted",
        "Accuracy",
        "Study Time",
        "Better questions. A brighter you.",
        "window.QB.startAllSubjectPractice()",
        "window.QB.openTestBuilder()",
        "window.QB.nkStartTodaysReview()",
        "window.QB.nav('bookmarks')",
    )
    missing = [item for item in required if item not in source]
    if missing:
        raise SystemExit(f"Approved Home marker missing after transform: {missing}")
    return source


def main() -> None:
    source = HTML.read_text(encoding="utf-8")
    updated = transform(source)
    HTML.write_text(updated, encoding="utf-8")
    print("HOME_APPROVED_REFERENCE_OK: screenshot-aligned Home installed; shared study engines untouched")


if __name__ == "__main__":
    main()
