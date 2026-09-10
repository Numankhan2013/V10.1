#!/usr/bin/env python3
"""Install the bounded Home Today’s Focus command center after Study Modules."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "app/src/main/assets/index.html"
STYLE_ID = "nk-home-command-center-v1"


RECOMMENDATION_HELPER = r'''  function nkHomeRecommendation(moduleFocus,due) {
    return moduleFocus?'module':due>0?'review':'practice';
  }

'''


OLD_FOCUS_LINE = "    const focus=moduleFocus?`Continue your ${moduleFocus.name}`:due?`Review ${due} due question${due===1?'':'s'}`:wrong?`Revisit ${wrong} missed question${wrong===1?'':'s'}`:'Build recall with 20 focused questions';"

NEW_FOCUS_LINE = r'''    const homeRecommendation=nkHomeRecommendation(moduleFocus,due);
    const focus=homeRecommendation==='module'?`Continue ${moduleFocus.name}`:homeRecommendation==='review'?`Review ${due} due question${due===1?'':'s'}`:'Build recall with 20 focused questions';'''


OLD_PANEL = '''<section class="nk-focus-panel"><div class="nk-kicker">TODAY'S FOCUS</div><h2>${esc(focus)}</h2><p>${moduleFocus?`${nkModuleProgress(moduleFocus).remaining} questions left in this saved study set.`:due?'Strengthen scheduled recall before adding new material.':wrong?'A second retrieval pass turns mistakes into memory.':'A compact mixed set is enough to build momentum.'}</p><div class="nk-focus-actions">${moduleFocus?`<button class="nk-focus-primary" onclick="window.QB.startStudyModule('${esc(moduleFocus.id)}')">${navIcon('book',18)}<span>Continue module</span>${navIcon('chevron',17)}</button><button onclick="window.QB.openStudyModuleBuilder()">Create module</button>`:`<button class="nk-focus-primary" onclick="window.QB.continuePractice()">${navIcon('book',18)}<span>Continue Practice</span>${navIcon('chevron',17)}</button>${due?`<button onclick="window.QB.startLibrary('review')">Review ${fmtNum(due)} Due</button>`:``}<button onclick="window.QB.startAllSubjectPractice()">Practice 20 Random Questions</button>`}<button onclick="window.QB.openTestBuilder()">Timed CBT</button></div></section>'''

NEW_PANEL = r'''<section class="nk-focus-panel nk-home-command-center" aria-labelledby="nk-home-focus-title"><div class="nk-focus-topline"><div class="nk-kicker">TODAY'S FOCUS</div><span class="nk-focus-status">Recommended now</span></div><h2 id="nk-home-focus-title">${esc(focus)}</h2><p>${homeRecommendation==='module'?`${nkModuleProgress(moduleFocus).remaining} questions remain in your most recently opened study set.`:homeRecommendation==='review'?'Strengthen scheduled recall before adding new material.':wrong?`${fmtNum(wrong)} missed question${wrong===1?' is':'s are'} waiting after this set.`:'A compact mixed set is enough to build momentum.'}</p><div class="nk-focus-primary-wrap">${homeRecommendation==='module'?`<button class="nk-focus-primary" onclick="window.QB.startStudyModule('${esc(moduleFocus.id)}')">${navIcon('book',19)}<span><small>RESUME SAVED MODULE</small><strong>Continue module</strong></span>${navIcon('chevron',18)}</button>`:homeRecommendation==='review'?`<button class="nk-focus-primary" onclick="window.QB.startLibrary('review')">${navIcon('clock',19)}<span><small>SPACED REVIEW</small><strong>Review ${fmtNum(due)} due</strong></span>${navIcon('chevron',18)}</button>`:`<button class="nk-focus-primary" onclick="window.QB.startAllSubjectPractice()">${navIcon('book',19)}<span><small>QUICK PRACTICE</small><strong>Practice 20 questions</strong></span>${navIcon('chevron',18)}</button>`}</div><div class="nk-focus-secondary" aria-label="Other study actions">${homeRecommendation==='module'?`<button onclick="window.QB.continuePractice()"><span>${navIcon('book',16)} Continue Practice</span><small>Next unattempted</small></button>${due?`<button onclick="window.QB.startLibrary('review')"><span>${navIcon('clock',16)} Review ${fmtNum(due)} Due</span><small>Scheduled recall</small></button>`:``}<button onclick="window.QB.startAllSubjectPractice()"><span>${navIcon('refresh',16)} Practice 20</span><small>Mixed questions</small></button>`:`<button onclick="window.QB.continuePractice()"><span>${navIcon('book',16)} Continue Practice</span><small>Next unattempted</small></button>${homeRecommendation==='review'?`<button onclick="window.QB.startAllSubjectPractice()"><span>${navIcon('refresh',16)} Practice 20</span><small>Mixed questions</small></button>`:``}`}<button onclick="window.QB.openTestBuilder()"><span>${navIcon('test',16)} Timed CBT</span><small>Exam conditions</small></button></div></section>'''

CSS = r'''<style id="nk-home-command-center-v1">
.nk-home-command-center{position:relative;overflow:hidden;background:linear-gradient(135deg,#28255f 0%,var(--nk114-indigo) 62%,#3c3979 100%)}
.nk-home-command-center:after{content:"";position:absolute;right:-68px;top:-86px;width:190px;height:190px;border:1px solid rgba(255,255,255,.09);border-radius:50%;pointer-events:none}
.nk-focus-topline{position:relative;z-index:1;display:flex;align-items:center;justify-content:space-between;gap:12px}.nk-focus-status{padding:5px 8px;border:1px solid rgba(255,255,255,.2);border-radius:7px;background:rgba(255,255,255,.08);color:#e8ebff;font-size:8px;font-weight:850;letter-spacing:.08em;text-transform:uppercase}
.nk-home-command-center h2,.nk-home-command-center>p,.nk-focus-primary-wrap,.nk-focus-secondary{position:relative;z-index:1}.nk-focus-primary-wrap{margin-top:17px}.nk-focus-primary-wrap .nk-focus-primary{width:100%;min-height:58px;padding:9px 12px;border:0;border-radius:11px;background:#fff;color:var(--nk114-indigo);display:grid;grid-template-columns:24px minmax(0,1fr) 18px;align-items:center;gap:9px;text-align:left;box-shadow:0 9px 24px rgba(9,7,43,.2)}.nk-focus-primary span small,.nk-focus-primary span strong{display:block}.nk-focus-primary span small{font-size:7.5px;line-height:1.2;letter-spacing:.09em;color:#777d9e}.nk-focus-primary span strong{margin-top:3px;font-size:12px;line-height:1.2}
.nk-focus-secondary{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:7px;margin-top:8px}.nk-focus-secondary button{min-height:49px;padding:8px 9px;border:1px solid rgba(255,255,255,.2);border-radius:10px;background:rgba(25,22,67,.3);color:#fff;text-align:left}.nk-focus-secondary button>span,.nk-focus-secondary button>small{display:block}.nk-focus-secondary button>span{display:flex;align-items:center;gap:5px;font-size:9.5px;font-weight:800}.nk-focus-secondary button>small{margin-top:4px;color:#bfc5e5;font-size:7.5px}
@media(max-width:480px){.nk-focus-topline{align-items:flex-start}.nk-focus-status{font-size:7px}.nk-focus-secondary{grid-template-columns:1fr 1fr}.nk-focus-secondary button:last-child:nth-child(3){grid-column:1/-1}.nk-focus-primary-wrap .nk-focus-primary{min-height:56px}}
@media(prefers-reduced-motion:reduce){.nk-home-command-center button{transition:none!important}}
</style>'''


def replace_once(source: str, old: str, new: str, label: str) -> str:
    count = source.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one target, found {count}")
    return source.replace(old, new, 1)


def transform(source: str) -> str:
    if f'id="{STYLE_ID}"' in source:
        return source
    if 'id="nk-custom-study-modules-v1"' not in source:
        raise SystemExit("Home command center must run after Custom Study Modules")
    source = replace_once(source, "  function dashboard() {", RECOMMENDATION_HELPER + "  function dashboard() {", "dashboard helper anchor")
    source = replace_once(source, OLD_FOCUS_LINE, NEW_FOCUS_LINE, "Home recommendation")
    source = replace_once(source, OLD_PANEL, NEW_PANEL, "Home focus panel")
    source = replace_once(source, "</head>", CSS + "\n</head>", "closing head")
    for marker in (STYLE_ID, "nkHomeRecommendation(moduleFocus,due)", "Recommended now", "Other study actions", "window.QB.openTestBuilder()"):
        if marker not in source:
            raise SystemExit(f"Home command center marker missing after transform: {marker}")
    return source


def main() -> None:
    source = HTML.read_text(encoding="utf-8")
    updated = transform(source)
    HTML.write_text(updated, encoding="utf-8")
    print("HOME_COMMAND_CENTER_OK: module, due-review, and Practice-20 priority installed")


if __name__ == "__main__":
    main()
