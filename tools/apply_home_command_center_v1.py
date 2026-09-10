#!/usr/bin/env python3
"""Install the approved Home-only mobile dashboard after Custom Study Modules.

This intentionally replaces the final Home dashboard composition, not merely one
legacy focus card. The shared shell/navigation and all Practice/CBT/Review/Topics
engines remain owned by their existing transforms.
"""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "app/src/main/assets/index.html"
STYLE_ID = "nk-home-command-center-v1"


DASHBOARD = r'''function dashboard() {
    const attempted=totalAttempted();
    const total=QUESTIONS.length;
    const due=pendingReviewCount();
    const wrong=wrongQuestions().length;
    const remaining=Math.max(0,total-attempted);
    const recent=(state.tests||[]).slice().sort((a,b)=>(b.createdAt||0)-(a.createdAt||0)).slice(0,3);
    const today=dayKey(new Date());
    let todayDone=0;
    for(const attempts of Object.values(state.attempts||{})) {
      for(const attempt of attempts||[]) {
        if(attempt&&attempt.ts&&dayKey(new Date(attempt.ts))===today) todayDone++;
      }
    }
    const dailyGoal=30;
    const goalPct=Math.max(0,Math.min(100,Math.round(todayDone/dailyGoal*100)));
    const continueTitle=due?`Review ${fmtNum(due)} due today`:remaining?`Continue ${activeSubject}`:'Keep recall moving';
    const continueMeta=due?`${fmtNum(due)} scheduled review${due===1?'':'s'} waiting`:remaining?`${fmtNum(remaining)} question${remaining===1?'':'s'} left in ${activeSubject}`:'Your current subject is fully attempted';
    return shell(`
      <main class="nk-home-approved-v1" aria-label="Home">
        <header class="nk-home-ref-head">
          <div>
            <h1>${greetingCopy()}</h1>
            <p>Keep going. Small steps make a big difference.</p>
          </div>
        </header>

        <section class="nk-home-command-center" aria-label="Continue learning and study actions">
          <div class="nk-focus-secondary">
            <article class="nk-home-ref-continue">
              <div class="nk-home-ref-book" aria-hidden="true">${navIcon('book',25)}</div>
              <div class="nk-home-ref-continue-copy">
                <span class="nk-home-ref-eyebrow">Recommended now</span>
                <small>CONTINUE LEARNING</small>
                <strong>${esc(continueTitle)}</strong>
                <p>${esc(continueMeta)}</p>
              </div>
              <button class="nk-home-ref-circle-action" onclick="window.QB.continuePractice()" aria-label="Continue Practice">${navIcon('chevron',18)}<span>Continue Practice</span></button>
            </article>

            <div class="nk-home-ref-quick-grid" aria-label="Quick study actions">
              <button class="nk-home-ref-quick nk-home-ref-practice nk-focus-primary" onclick="window.QB.startAllSubjectPractice()"><span>${navIcon('book',21)}</span><strong>Practice 20 Random Questions</strong><small>Quick practice</small></button>
              <button class="nk-home-ref-quick" onclick="window.QB.openTestBuilder()"><span>${navIcon('test',21)}</span><strong>Timed Test</strong><small>Timed CBT · exam mode</small></button>
              <button class="nk-home-ref-quick" onclick="window.QB.openStudyModuleBuilder()"><span>${navIcon('refresh',21)}</span><strong>Custom Test</strong><small>Your own study set</small></button>
              <button class="nk-home-ref-quick" onclick="window.QB.startLibrary('review')"><span>${navIcon('clock',21)}</span><strong>Review</strong><small>${due?`${fmtNum(due)} due`:(wrong?`${fmtNum(wrong)} missed`:'Past questions')}</small></button>
            </div>
          </div>
        </section>

        <section class="nk-home-ref-goal" aria-labelledby="nk-home-goal-title">
          <div class="nk-home-ref-section-title" id="nk-home-goal-title">Today's goal</div>
          <div class="nk-home-ref-goal-card">
            <div class="nk-home-ref-ring" style="--nk-goal:${goalPct}%"><div><strong>${fmtNum(todayDone)}/${dailyGoal}</strong><span>questions</span></div></div>
            <div class="nk-home-ref-goal-copy"><strong>${todayDone>=dailyGoal?'Goal complete.':'You’re on track!'}</strong><p>${todayDone>=dailyGoal?'Excellent work today. Keep the momentum.':`${fmtNum(Math.max(0,dailyGoal-todayDone))} questions to reach today’s target.`}</p></div>
          </div>
        </section>

        <section class="nk-home-ref-recent" aria-labelledby="nk-home-recent-title">
          <div class="nk-home-ref-section-head"><h2 id="nk-home-recent-title">Recent Activity</h2><button onclick="window.QB.nav('tests')">See all</button></div>
          <div class="nk-home-ref-activity-list">
            ${recent.length?recent.map(testRow).join(''):`<div class="nk-home-ref-empty"><span>${navIcon('clock',20)}</span><div><strong>No recent test activity yet</strong><p>Start a quick practice set or timed test when you’re ready.</p></div></div>`}
          </div>
        </section>
      </main>`, 'dashboard');
  }
'''


CSS = r'''<style id="nk-home-command-center-v1">
/* Approved Home reference: compact mobile hierarchy, Home only. */
body:has(.nk-home-approved-v1) .topbar{display:none!important}
body:has(.nk-home-approved-v1){background:#f6f7fb}
.nk-home-approved-v1{max-width:760px;margin:0 auto;padding:14px 0 30px;color:#171a58}
.nk-home-ref-head{padding:8px 2px 14px}
.nk-home-ref-head h1{margin:0;font-size:25px;line-height:1.08;font-weight:900;letter-spacing:-.65px;color:#151852}
.nk-home-ref-head p{margin:5px 0 0;font-size:11px;line-height:1.45;color:#8589ac}
.nk-home-command-center{margin:0}
.nk-focus-secondary{display:block}
.nk-home-ref-continue{display:grid;grid-template-columns:45px minmax(0,1fr) 40px;gap:11px;align-items:center;min-height:96px;padding:14px 13px;border:1px solid #e4e5f2;border-radius:14px;background:linear-gradient(105deg,#f4f2ff 0%,#f1f4ff 100%);box-shadow:0 7px 22px rgba(54,52,120,.06)}
.nk-home-ref-book{width:43px;height:43px;border-radius:12px;display:grid;place-items:center;color:#624ef4;background:#e8e3ff}
.nk-home-ref-continue-copy{min-width:0}.nk-home-ref-continue-copy span,.nk-home-ref-continue-copy small,.nk-home-ref-continue-copy strong{display:block}
.nk-home-ref-eyebrow{width:max-content;max-width:100%;margin-bottom:4px;padding:3px 6px;border-radius:5px;background:#e7e4ff;color:#6554d9;font-size:6.8px!important;line-height:1.1;font-weight:900;letter-spacing:.08em;text-transform:uppercase}
.nk-home-ref-continue-copy small{font-size:7.5px;line-height:1.1;font-weight:800;letter-spacing:.07em;color:#8185a6}
.nk-home-ref-continue-copy strong{overflow:hidden;text-overflow:ellipsis;white-space:nowrap;margin-top:4px;font-size:13px;line-height:1.2;color:#20235f}
.nk-home-ref-continue-copy p{margin:4px 0 0;font-size:8.5px;line-height:1.35;color:#8589a8}
.nk-home-ref-circle-action{position:relative;width:36px;height:36px;border:0;border-radius:50%;display:grid;place-items:center;background:linear-gradient(135deg,#6752f5,#425ce7);color:#fff;box-shadow:0 6px 14px rgba(77,75,220,.25)}
.nk-home-ref-circle-action>span{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0}
.nk-home-ref-quick-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:8px;margin-top:10px}
.nk-home-ref-quick{min-height:82px;padding:10px 7px 9px;border:1px solid #e5e7f0;border-radius:12px;background:#fff;color:#272a65;text-align:center;box-shadow:0 3px 12px rgba(39,42,101,.035)}
.nk-home-ref-quick>span{width:31px;height:31px;margin:0 auto 6px;border-radius:9px;display:grid;place-items:center;background:#eef0ff;color:#5660ea}
.nk-home-ref-quick:nth-child(2)>span{background:#eaf9f1;color:#19966b}.nk-home-ref-quick:nth-child(3)>span{background:#eef2ff;color:#416cde}.nk-home-ref-quick:nth-child(4)>span{background:#fff0ed;color:#e55e55}
.nk-home-ref-quick strong,.nk-home-ref-quick small{display:block}.nk-home-ref-quick strong{font-size:9px;line-height:1.22;font-weight:850}.nk-home-ref-quick small{margin-top:3px;font-size:7.2px;line-height:1.2;color:#979ab1}
.nk-home-ref-section-title,.nk-home-ref-section-head h2{font-size:14px;line-height:1.2;font-weight:900;color:#1c205d}
.nk-home-ref-goal{margin-top:21px}.nk-home-ref-goal-card{display:grid;grid-template-columns:86px minmax(0,1fr);gap:15px;align-items:center;margin-top:8px;padding:13px 14px;border:1px solid #e6e8f0;border-radius:13px;background:#fff}
.nk-home-ref-ring{width:68px;height:68px;border-radius:50%;display:grid;place-items:center;background:conic-gradient(#6555ed var(--nk-goal),#eceef7 0)}
.nk-home-ref-ring:before{content:"";grid-area:1/1;width:53px;height:53px;border-radius:50%;background:#fff}.nk-home-ref-ring>div{grid-area:1/1;position:relative;text-align:center}.nk-home-ref-ring strong,.nk-home-ref-ring span{display:block}.nk-home-ref-ring strong{font-size:12px;line-height:1;font-weight:900}.nk-home-ref-ring span{margin-top:4px;font-size:6.8px;color:#8a8eaa}
.nk-home-ref-goal-copy strong{font-size:11px}.nk-home-ref-goal-copy p{margin:4px 0 0;font-size:8.5px;line-height:1.45;color:#8a8da8}
.nk-home-ref-recent{margin-top:22px}.nk-home-ref-section-head{display:flex;align-items:center;justify-content:space-between;gap:12px;margin-bottom:8px}.nk-home-ref-section-head h2{margin:0}.nk-home-ref-section-head button{border:0;background:transparent;color:#5e52df;font-size:9px;font-weight:850}
.nk-home-ref-activity-list{display:grid;gap:7px}.nk-home-ref-activity-list .recent-row{min-height:62px;padding:9px 11px;border:1px solid #e7e8ef!important;border-radius:12px!important;background:#fff!important;box-shadow:none!important}.nk-home-ref-activity-list .recent-row:hover{background:#fbfbfe!important}
.nk-home-ref-empty{display:grid;grid-template-columns:36px 1fr;gap:10px;align-items:center;padding:13px;border:1px solid #e7e8ef;border-radius:12px;background:#fff}.nk-home-ref-empty>span{width:34px;height:34px;border-radius:10px;display:grid;place-items:center;background:#eef0ff;color:#5862df}.nk-home-ref-empty strong{font-size:10px}.nk-home-ref-empty p{margin:3px 0 0;font-size:8px;color:#8b8fa9}
@media(max-width:560px){.nk-home-approved-v1{padding-top:10px}.nk-home-ref-head{padding-left:1px}.nk-home-ref-head h1{font-size:23px}.nk-home-ref-continue{min-height:91px;padding:12px 11px}.nk-home-ref-quick-grid{gap:6px}.nk-home-ref-quick{min-height:78px;padding:9px 5px}.nk-home-ref-quick strong{font-size:8.5px}.nk-home-ref-goal-card{grid-template-columns:78px 1fr}}
@media(max-width:360px){.nk-home-ref-quick-grid{grid-template-columns:1fr 1fr}.nk-home-ref-quick{min-height:70px}.nk-home-ref-continue{grid-template-columns:40px minmax(0,1fr) 36px}.nk-home-ref-book{width:39px;height:39px}.nk-home-ref-circle-action{width:34px;height:34px}}
@media(prefers-reduced-motion:reduce){.nk-home-approved-v1 button{transition:none!important;animation:none!important}}
</style>'''


def replace_function(source: str, name: str, replacement: str) -> str:
    start = source.find(f"function {name}(")
    if start < 0:
        raise SystemExit(f"{name} not found")
    brace = source.find("{", start)
    if brace < 0:
        raise SystemExit(f"{name} opening brace not found")
    depth = 0
    quote = None
    escaped = False
    template_depth = 0
    for index in range(brace, len(source)):
        char = source[index]
        if quote:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote and (quote != "`" or template_depth == 0):
                quote = None
            elif quote == "`" and source[index:index + 2] == "${":
                template_depth += 1
            elif quote == "`" and char == "}" and template_depth:
                template_depth -= 1
            continue
        if char in "'\"`":
            quote = char
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return source[:start] + replacement.rstrip() + source[index + 1:]
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
        "Recommended now",
        "Continue Learning",
        "Practice 20 Random Questions",
        "Timed Test",
        "Timed CBT",
        "Custom Test",
        "Today's goal",
        "Recent Activity",
        "window.QB.continuePractice()",
        "window.QB.startAllSubjectPractice()",
        "window.QB.openTestBuilder()",
        "window.QB.openStudyModuleBuilder()",
        "window.QB.startLibrary('review')",
    )
    missing = [item for item in required if item not in source]
    if missing:
        raise SystemExit(f"Approved Home marker missing after transform: {missing}")
    return source


def main() -> None:
    source = HTML.read_text(encoding="utf-8")
    updated = transform(source)
    HTML.write_text(updated, encoding="utf-8")
    print("HOME_APPROVED_REFERENCE_OK: full Home hierarchy installed; shared study engines untouched")


if __name__ == "__main__":
    main()
