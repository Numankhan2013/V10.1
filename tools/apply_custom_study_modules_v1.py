#!/usr/bin/env python3
"""Install persistent Custom Study Modules after the V11.4 product layer."""

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "app/src/main/assets/index.html"
CORE = ROOT / "tools/study_modules_core.js"
STYLE_ID = "nk-custom-study-modules-v1"


CSS = r'''<style id="nk-custom-study-modules-v1">
.nk-study-sets{margin-top:22px}.nk-study-set-list{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:9px}.nk-study-set-card{position:relative;padding:13px;background:#fff;border:1px solid var(--nk114-line);border-radius:14px}.nk-study-set-main{display:grid;grid-template-columns:34px minmax(0,1fr) 32px;gap:9px;align-items:start}.nk-study-set-icon{width:32px;height:32px;border-radius:9px;display:grid;place-items:center;background:#eef1ff;color:var(--nk114-indigo)}.nk-study-set-main strong,.nk-study-set-main small,.nk-study-set-main em{display:block}.nk-study-set-main strong{font-size:12px}.nk-study-set-main small{margin-top:3px;color:var(--nk114-muted);font-size:9px;line-height:1.35}.nk-study-set-main em{width:max-content;max-width:100%;margin-top:6px;padding:3px 6px;border-radius:6px;background:#f2f4f8;color:#59617a;font-size:8px;font-style:normal;font-weight:800}.nk-study-set-main details{position:relative}.nk-study-set-main summary{width:32px;height:32px;display:grid;place-items:center;list-style:none;cursor:pointer;color:#667089}.nk-study-set-main summary::-webkit-details-marker{display:none}.nk-study-set-main details>div{position:absolute;right:0;top:34px;z-index:20;width:120px;padding:5px;background:#fff;border:1px solid var(--nk114-line);border-radius:10px;box-shadow:0 12px 32px rgba(20,25,55,.16)}.nk-study-set-main details button{width:100%;min-height:34px;padding:0 8px;border:0;border-radius:7px;background:#fff;text-align:left;color:var(--nk114-ink);font-size:9px;font-weight:750}.nk-study-set-main details button:hover{background:#f4f5f8}.nk-study-set-main details button.is-danger{color:var(--nk114-red)}.nk-study-set-progress{display:flex;justify-content:space-between;gap:8px;margin:11px 0 6px;color:var(--nk114-muted);font-size:9px}.nk-study-set-progress b{color:var(--nk114-ink)}.nk-study-set-card>p{margin:6px 0 0;color:var(--nk114-amber);font-size:8.5px}.nk-study-set-action{width:100%;min-height:39px;margin-top:11px;border:1px solid #d7dcf0;border-radius:9px;background:#f7f8ff;color:var(--nk114-indigo);display:flex;align-items:center;justify-content:center;gap:5px;font-size:10px;font-weight:850}.nk-study-set-empty{min-height:78px;padding:13px;background:#fff;border:1px solid var(--nk114-line);border-radius:14px;display:grid;grid-template-columns:34px minmax(0,1fr) auto;align-items:center;gap:10px}.nk-study-set-empty>span{width:34px;height:34px;border-radius:10px;background:#eef1ff;color:var(--nk114-indigo);display:grid;place-items:center}.nk-study-set-empty strong{font-size:11.5px}.nk-study-set-empty p{margin:3px 0 0;color:var(--nk114-muted);font-size:9px}.nk-study-set-empty button{min-height:38px;padding:0 11px;border:0;border-radius:9px;background:var(--nk114-indigo);color:#fff;font-size:9.5px;font-weight:800}
.nk-module-builder{max-width:760px}.nk-module-stepper{display:grid;grid-template-columns:repeat(4,1fr);margin:18px 0 12px}.nk-module-stepper span{position:relative;display:flex;flex-direction:column;align-items:center;gap:5px;color:#9298aa;font-size:8.5px;font-weight:750}.nk-module-stepper span:before{content:"";position:absolute;top:13px;left:-50%;right:50%;height:2px;background:#e1e4ec}.nk-module-stepper span:first-child:before{display:none}.nk-module-stepper i{position:relative;z-index:1;width:27px;height:27px;border-radius:50%;background:#e9ebf1;display:grid;place-items:center;font-style:normal}.nk-module-stepper .is-current,.nk-module-stepper .is-done{color:var(--nk114-indigo)}.nk-module-stepper .is-current i,.nk-module-stepper .is-done i{background:var(--nk114-indigo);color:#fff}.nk-module-stepper .is-done:before,.nk-module-stepper .is-current:before{background:var(--nk114-indigo)}.nk-module-builder-card{min-height:300px;padding:18px;background:#fff;border:1px solid var(--nk114-line);border-radius:15px}.nk-module-choice-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:9px}.nk-module-subject{position:relative;min-height:112px;padding:13px;border:1px solid var(--nk114-line);border-radius:13px;background:#fff;text-align:left;color:var(--nk114-ink)}.nk-module-subject>span{width:37px;height:37px;border-radius:10px;display:grid;place-items:center;background:#f2f3f7;color:#52617c}.nk-module-subject.is-biochemistry>span{background:#f9edf6;color:var(--nk114-magenta)}.nk-module-subject.is-physiology>span{background:#fff0ee;color:#c2534b}.nk-module-subject.is-anatomy>span{background:#edf7fc;color:#277899}.nk-module-subject strong,.nk-module-subject small{display:block}.nk-module-subject strong{margin-top:9px;font-size:12px}.nk-module-subject small{margin-top:3px;color:var(--nk114-muted);font-size:8.5px}.nk-module-subject>i{position:absolute;right:9px;top:9px;width:21px;height:21px;border:1px solid #ccd2df;border-radius:7px;display:grid;place-items:center;color:transparent}.nk-module-subject.is-selected{border-color:#819be5;background:#fafaff;box-shadow:inset 0 0 0 1px #819be5}.nk-module-subject.is-selected>i{background:var(--nk114-indigo);border-color:var(--nk114-indigo);color:#fff}.nk-module-select-tools{display:flex;align-items:center;gap:8px;margin-bottom:9px}.nk-module-select-tools button{min-height:34px;padding:0 9px;border:1px solid var(--nk114-line);border-radius:8px;background:#fff;color:#4b6093;font-size:9px;font-weight:800}.nk-module-select-tools span{margin-left:auto;color:var(--nk114-muted);font-size:9px}.nk-module-topic-groups{max-height:390px;overflow:auto;border:1px solid var(--nk114-line);border-radius:12px}.nk-module-topic-group+ .nk-module-topic-group{border-top:7px solid #f4f5f8}.nk-module-topic-group>header{position:sticky;top:0;z-index:2;min-height:43px;padding:7px 10px;background:#fafbfe;border-bottom:1px solid var(--nk114-line);display:grid;grid-template-columns:28px 1fr;gap:8px;align-items:center}.nk-module-topic-group>header>span{width:28px;height:28px;border-radius:8px;display:grid;place-items:center}.nk-module-topic-group header strong,.nk-module-topic-group header small{display:block}.nk-module-topic-group header strong{font-size:10.5px}.nk-module-topic-group header small{font-size:8px;color:var(--nk114-muted)}.nk-module-topic{width:100%;min-height:50px;padding:8px 10px;border:0;border-bottom:1px solid var(--nk114-line);background:#fff;display:grid;grid-template-columns:24px 1fr;align-items:center;gap:8px;text-align:left;color:var(--nk114-ink)}.nk-module-topic:last-child{border-bottom:0}.nk-module-topic strong,.nk-module-topic small{display:block}.nk-module-topic strong{font-size:10.5px}.nk-module-topic small{margin-top:2px;color:var(--nk114-muted);font-size:8px}.nk-module-check{width:21px;height:21px;border:1px solid #cbd1df;border-radius:6px;display:grid;place-items:center;color:transparent}.nk-module-topic.is-selected{background:#fafbff}.nk-module-topic.is-selected .nk-module-check{background:var(--nk114-blue);border-color:var(--nk114-blue);color:#fff}.nk-module-pool-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:8px}.nk-module-pool-grid button{min-height:70px;padding:11px;border:1px solid var(--nk114-line);border-radius:11px;background:#fff;text-align:left;color:var(--nk114-ink)}.nk-module-pool-grid button.is-selected{border-color:#789cf0;background:#f1f5ff}.nk-module-pool-grid strong,.nk-module-pool-grid small{display:block}.nk-module-pool-grid strong{font-size:11px}.nk-module-pool-grid small{margin-top:4px;color:var(--nk114-muted);font-size:8.5px}.nk-module-count-block{margin-top:18px;padding-top:15px;border-top:1px solid var(--nk114-line)}.nk-module-count-block>strong{font-size:11px}.nk-module-count-presets{display:grid;grid-template-columns:repeat(4,1fr);gap:7px;margin-top:8px}.nk-module-count-presets button{min-height:40px;border:1px solid var(--nk114-line);border-radius:9px;background:#fff;color:var(--nk114-ink);font-size:10px;font-weight:800}.nk-module-count-presets button.is-selected{background:var(--nk114-indigo);border-color:var(--nk114-indigo);color:#fff}.nk-module-count-block label,.nk-module-name{display:block;margin-top:10px;color:var(--nk114-muted);font-size:9px;font-weight:750}.nk-module-count-block input,.nk-module-name input{width:100%;height:44px;margin-top:6px;padding:0 11px;border:1px solid var(--nk114-line);border-radius:10px;background:#fff;color:var(--nk114-ink);font:inherit}.nk-module-count-block p{margin:9px 0 0;padding:9px 10px;border-radius:9px;background:#f1f6ff;color:#3d5f9e;font-size:9px}.nk-module-count-block p.is-error{background:#fff1f2;color:var(--nk114-red)}.nk-module-name{margin-top:0;font-size:10px}.nk-module-name input{font-size:12px}.nk-module-review-card{display:grid;grid-template-columns:1fr 1fr;gap:9px;margin-top:14px}.nk-module-review-card>div{padding:13px;border:1px solid var(--nk114-line);border-radius:11px;background:#fafbfe}.nk-module-review-card small,.nk-module-review-card strong,.nk-module-review-card p{display:block}.nk-module-review-card small{font-size:8px;color:var(--nk114-muted)}.nk-module-review-card strong{margin-top:5px;font-size:11px}.nk-module-review-card p{margin:4px 0 0;color:var(--nk114-muted);font-size:8.5px}.nk-module-warning{margin-top:10px;padding:11px;border:1px solid #f0ddb0;border-radius:10px;background:#fff7e7;color:#7e5b18;font-size:9px;line-height:1.45}.nk-module-builder-actions{display:grid;grid-template-columns:1fr auto;align-items:center;gap:8px;margin-top:12px}.nk-module-builder-actions>button,.nk-module-final-actions button{min-height:44px;padding:0 14px;border:1px solid var(--nk114-line);border-radius:10px;background:#fff;color:var(--nk114-ink);font-size:10.5px;font-weight:800}.nk-module-builder-actions .is-primary,.nk-module-final-actions .is-primary{background:var(--nk114-indigo);border-color:var(--nk114-indigo);color:#fff}.nk-module-final-actions{display:flex;gap:8px}.nk-module-builder-actions button:disabled{opacity:.45}.nk-module-session-context{min-height:48px;margin:0 0 16px;padding:8px 11px;border:1px solid #d9dff1;border-radius:12px;background:#f6f7ff;display:grid;grid-template-columns:30px 1fr auto;align-items:center;gap:8px;color:var(--nk-indigo)}.nk-module-session-context>span{width:29px;height:29px;border-radius:8px;background:#e9edff;display:grid;place-items:center}.nk-module-session-context small,.nk-module-session-context strong{display:block}.nk-module-session-context small{font-size:8px;letter-spacing:.08em;color:#66729a}.nk-module-session-context strong{font-size:12px;margin-top:2px}.nk-module-session-context em{font-size:9px;font-style:normal;font-weight:800;color:#5f698b}.nk-module-result-actions{display:flex;gap:8px;margin-bottom:10px}.nk-module-result-actions button{min-height:40px;padding:0 11px;border:1px solid var(--nk114-line);border-radius:9px;background:#fff;color:var(--nk114-indigo);font-size:9.5px;font-weight:800}.nk-module-topic-result{min-height:55px;padding:9px 12px;border-bottom:1px solid var(--nk114-line);display:grid;grid-template-columns:1fr auto;align-items:center;gap:8px}.nk-module-topic-result:last-child{border-bottom:0}.nk-module-topic-result strong,.nk-module-topic-result small{display:block}.nk-module-topic-result strong{font-size:10.5px}.nk-module-topic-result small{margin-top:3px;color:var(--nk114-muted);font-size:8.5px}.nk-module-topic-result>b{font-size:10px}
@media(max-width:620px){.nk-study-set-list{grid-template-columns:1fr}.nk-study-set-empty{grid-template-columns:34px 1fr}.nk-study-set-empty button{grid-column:1/-1}.nk-module-choice-grid{grid-template-columns:1fr}.nk-module-subject{min-height:76px;display:grid;grid-template-columns:38px 1fr;column-gap:9px}.nk-module-subject strong{margin-top:0;align-self:end}.nk-module-subject small{grid-column:2}.nk-module-pool-grid{grid-template-columns:1fr 1fr}.nk-module-builder-card{padding:14px}.nk-module-stepper b{font-size:7.5px}.nk-module-review-card{grid-template-columns:1fr}.nk-module-builder-actions{grid-template-columns:1fr}.nk-module-builder-actions>span{display:none}.nk-module-builder-actions>button{width:100%}.nk-module-final-actions{display:grid;grid-template-columns:1fr 1fr}.nk-module-result-actions{display:grid;grid-template-columns:1fr}.nk-module-result-actions button{width:100%}}
</style>'''


def replace_function(source: str, name: str, replacement: str) -> str:
    start = source.find(f"function {name}(")
    if start < 0:
        raise SystemExit(f"{name} not found")
    brace = source.find("{", start)
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


def function_block(source: str, name: str) -> tuple[int, int, str]:
    token = f"function {name}("
    start = source.find(token)
    if start < 0:
        raise SystemExit(f"{name} not found")
    sentinel = f"__NK_FUNCTION_SENTINEL_{name}__"
    replaced = replace_function(source, name, sentinel)
    sentinel_at = replaced.find(sentinel)
    removed = len(source) - (len(replaced) - len(sentinel))
    return start, start + removed, source[start:start + removed]


def replace_once(source: str, old: str, new: str, label: str) -> str:
    count = source.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one target, found {count}")
    return source.replace(old, new, 1)


def transform(source: str) -> str:
    if 'id="nk-whole-app-vision-v114"' not in source or 'id="nk-session-experience-v114"' not in source:
        raise SystemExit("Custom Study Modules must run after V11.4 and the protected session experience")
    if f'id="{STYLE_ID}"' in source and "/* NK_CUSTOM_STUDY_MODULES_V1_START */" in source:
        return source


    source = re.sub(r'/\* NK_CUSTOM_STUDY_MODULES_V1_START \*/.*?/\* NK_CUSTOM_STUDY_MODULES_V1_END \*/\s*', '', source, flags=re.S)
    source = re.sub(rf'<style id="{STYLE_ID}">.*?</style>\s*', '', source, flags=re.S)

    if "studyModules: []" not in source:
        source = replace_once(source, "    tests: [],\n    activeSession: null,", "    tests: [],\n    studyModules: [],\n    activeSession: null,", "default module state")
    if "studyModules: Array.isArray(parsed.studyModules)" not in source:
        source = replace_once(source, "        tests: Array.isArray(parsed.tests) ? parsed.tests : []", "        tests: Array.isArray(parsed.tests) ? parsed.tests : [],\n        studyModules: Array.isArray(parsed.studyModules) ? parsed.studyModules : []", "module state load")
    if "nkNormalizeStudyModules();\n  let route" not in source:
        source = replace_once(source, "  let state = loadState();\n  let route", "  let state = loadState();\n  nkNormalizeStudyModules();\n  let route", "module state normalization")
    if "nkSyncModuleFromSession(); localStorage.setItem" not in source:
        source = replace_once(source, "try { localStorage.setItem(LS_KEY, JSON.stringify(state)); }", "try { nkSyncModuleFromSession(); localStorage.setItem(LS_KEY, JSON.stringify(state)); }", "module save synchronization")

    anchor = "  function richText(text) {"
    if source.count(anchor) != 1:
        raise SystemExit("Study module insertion point not found exactly once")
    core = CORE.read_text(encoding="utf-8").strip() + "\n\n"
    source = source.replace(anchor, core + anchor, 1)

    source = replace_once(
        source,
        "const focus=due?`Review ${due} due question${due===1?'':'s'}`:wrong?`Revisit ${wrong} missed question${wrong===1?'':'s'}`:'Build recall with 20 focused questions';",
        "const moduleFocus=nkPriorityStudyModule();\n    const focus=moduleFocus?`Continue your ${moduleFocus.name}`:due?`Review ${due} due question${due===1?'':'s'}`:wrong?`Revisit ${wrong} missed question${wrong===1?'':'s'}`:'Build recall with 20 focused questions';",
        "Home module priority",
    )
    old_focus = "<p>${due?'Strengthen scheduled recall before adding new material.':wrong?'A second retrieval pass turns mistakes into memory.':'A compact mixed set is enough to build momentum.'}</p><div class=\"nk-focus-actions\"><button class=\"nk-focus-primary\" onclick=\"window.QB.continuePractice()\">${navIcon('book',18)}<span>Continue Practice</span>${navIcon('chevron',17)}</button>${due?`<button onclick=\"window.QB.startLibrary('review')\">Review ${fmtNum(due)} Due</button>`:``}<button onclick=\"window.QB.startAllSubjectPractice()\">Practice 20 Random Questions</button><button onclick=\"window.QB.openTestBuilder()\">Timed CBT</button></div>"
    new_focus = "<p>${moduleFocus?`${nkModuleProgress(moduleFocus).remaining} questions left in this saved study set.`:due?'Strengthen scheduled recall before adding new material.':wrong?'A second retrieval pass turns mistakes into memory.':'A compact mixed set is enough to build momentum.'}</p><div class=\"nk-focus-actions\">${moduleFocus?`<button class=\"nk-focus-primary\" onclick=\"window.QB.startStudyModule('${esc(moduleFocus.id)}')\">${navIcon('book',18)}<span>Continue module</span>${navIcon('chevron',17)}</button><button onclick=\"window.QB.openStudyModuleBuilder()\">Create module</button>`:`<button class=\"nk-focus-primary\" onclick=\"window.QB.continuePractice()\">${navIcon('book',18)}<span>Continue Practice</span>${navIcon('chevron',17)}</button>${due?`<button onclick=\"window.QB.startLibrary('review')\">Review ${fmtNum(due)} Due</button>`:``}<button onclick=\"window.QB.startAllSubjectPractice()\">Practice 20 Random Questions</button>`}<button onclick=\"window.QB.openTestBuilder()\">Timed CBT</button></div>"
    source = replace_once(source, old_focus, new_focus, "Home focus module action")
    source = replace_once(
        source,
        "      <section class=\"nk-section\"><div class=\"nk-section-head\"><div><div class=\"nk-kicker\">STUDY LIBRARY</div><h2>Subjects</h2></div>",
        "      ${nkStudySetsSection()}\n      <section class=\"nk-section\"><div class=\"nk-section-head\"><div><div class=\"nk-kicker\">STUDY LIBRARY</div><h2>Subjects</h2></div>",
        "Home study sets section",
    )
    source = replace_once(
        source,
        "<section class=\"nk-settings-group\"><div class=\"nk-kicker\">STUDY</div><div>${row('test','Timed CBT'",
        "<section class=\"nk-settings-group\"><div class=\"nk-kicker\">STUDY</div><div>${row('book','Create module','Build a reusable focused study set','window.QB.openStudyModuleBuilder()','is-violet')}${row('test','Timed CBT'",
        "More create-module entry",
    )

    practice_start, practice_end, practice = function_block(source, "practicePage")
    practice = replace_once(practice, '<section class="question-card">${nkQuestionContext(q)}', '<section class="question-card">${s.studyModuleId?nkStudyModuleSessionContext(s):\'\'}${nkQuestionContext(q)}', "module session identity")
    source = source[:practice_start] + practice + source[practice_end:]

    finish_start, finish_end, finish = function_block(source, "finishPracticeSession")
    if "studyModuleId:s.studyModuleId||null" not in finish:
        finish = replace_once(finish, "      kind:'practice',", "      kind:'practice', studyModuleId:s.studyModuleId||null,", "module result link")
    if "nkCompleteStudyModule(s.studyModuleId,test)" not in finish:
        finish = replace_once(finish, "    state.activeSession=null;", "    if(s.studyModuleId) nkCompleteStudyModule(s.studyModuleId,test);\n    state.activeSession=null;", "module completion")
    source = source[:finish_start] + finish + source[finish_end:]

    submit_practice_start, submit_practice_end, submit_practice = function_block(source, "submitPractice")
    submit_practice = replace_once(
        submit_practice,
        "recordAttempt(q.id,sel,s.questionTimes[q.id]||0,'practice')",
        "recordAttempt(q.id,sel,s.questionTimes[q.id]||0,s.studyModuleId?'study-module':'practice')",
        "module attempt source",
    )
    source = source[:submit_practice_start] + submit_practice + source[submit_practice_end:]

    review_start, review_end, session_review = function_block(source, "openSessionReview")
    session_review = replace_once(session_review, "    const total=s.questionIds.length;", "    const moduleSession=Boolean(s.studyModuleId);\n    const total=s.questionIds.length;", "module session review flag")
    session_review = replace_once(session_review, "const heading=s.mode==='exam'?'Review before submitting':'Review before finishing';", "const heading=s.mode==='exam'?'Review before submitting':moduleSession?'Module progress':'Review before finishing';", "module review heading")
    session_review = replace_once(session_review, "const sub=s.mode==='exam'\n      ? 'Check answered, skipped, and unanswered questions. You can jump back to any question before submitting the test.'\n      : 'Check the questions you answered and jump back to any unanswered question before finishing the session.';", "const sub=s.mode==='exam'\n      ? 'Check answered, skipped, and unanswered questions. You can jump back to any question before submitting the test.'\n      : moduleSession?'Your progress is saved after every answer. Continue later, or complete the module when you are ready.':'Check the questions you answered and jump back to any unanswered question before finishing the session.';", "module review guidance")
    session_review = replace_once(session_review, "const actionLabel=s.mode==='exam'?'Submit Test':'Finish Session';", "const actionLabel=s.mode==='exam'?'Submit Test':moduleSession?(unanswered?'Save & exit':'Complete module'):'Finish Session';", "module review action")
    session_review = replace_once(session_review, "    const box=document.createElement('div');", "    const moduleFinish=moduleSession&&unanswered?`<button type=\"button\" class=\"ghost-btn\" onclick=\"window.QB.finishStudyModuleEarly()\">Finish with ${unanswered} omitted</button>`:'';\n    const box=document.createElement('div');", "module early finish")
    session_review = replace_once(session_review, "${backBtn}${unansweredBtn}<button type=\"button\" class=\"primary-btn\"", "${backBtn}${unansweredBtn}${moduleFinish}<button type=\"button\" class=\"primary-btn\"", "module review controls")
    source = source[:review_start] + session_review + source[review_end:]

    submit_start, submit_end, review_submit = function_block(source, "sessionReviewSubmit")
    review_submit = "function sessionReviewSubmit(){const s=state.activeSession;if(!s)return;closeSessionReview();if(s.mode==='exam')submitExam(false);else if(s.studyModuleId&&s.questionIds.some(id=>!s.submitted?.[id]))exitStudyModule();else endSession();}"
    source = source[:submit_start] + review_submit + source[submit_end:]

    render_start, render_end, render = function_block(source, "render")
    render = replace_once(render, "    else if(route.page==='practice') out=practicePage();", "    else if(route.page==='module-builder') out=studyModuleBuilderPage();\n    else if(route.page==='practice') out=practicePage();", "module builder route")
    source = source[:render_start] + render + source[render_end:]

    result_start, result_end, result = function_block(source, "resultPage")
    result = replace_once(result, "const isPractice=t.kind==='practice',score=", "const isPractice=t.kind==='practice',studyModule=t.studyModuleId?nkFindStudyModule(t.studyModuleId):null,score=", "module result lookup")
    result = replace_once(result, "isPractice?'Practice analysis':'Test analysis'", "studyModule?'Module analysis':isPractice?'Practice analysis':'Test analysis'", "module result title")
    result = replace_once(result, "      <section class=\"nk-section\"><div class=\"nk-section-head\"><div><div class=\"nk-kicker\">QUESTION REVIEW</div>", "      ${studyModule?nkModuleResultExtras(t,studyModule):''}\n      <section class=\"nk-section\"><div class=\"nk-section-head\"><div><div class=\"nk-kicker\">QUESTION REVIEW</div>", "module result details")
    source = source[:result_start] + result + source[result_end:]

    export_match = re.search(r"window\.QB=\{([^\n]+)\};", source)
    if not export_match:
        raise SystemExit("Canonical QB export not found")
    exports = export_match.group(1)
    additions = "openStudyModuleBuilder,nkToggleModuleSubject,nkToggleModuleTopic,nkSetAllModuleTopics,nkSetModulePool,nkSetModuleCount,nkSetCustomModuleCount,nkSetModuleName,nkModuleBuilderStep,nkCreateStudyModule,startStudyModule,exitStudyModule,finishStudyModuleEarly,restartStudyModule,renameStudyModule,deleteStudyModule,"
    if "openStudyModuleBuilder" not in exports:
        exports = additions + exports
        source = source[:export_match.start(1)] + exports + source[export_match.end(1):]

    if "</head>" not in source:
        raise SystemExit("Closing head not found")
    source = source.replace("</head>", CSS + "\n</head>", 1)

    required = [
        "studyModules: []", "nkSyncModuleFromSession(); localStorage.setItem",
        "function nkSelectModuleQuestionIds", "function studyModuleBuilderPage",
        "function startStudyModule", "function nkCompleteStudyModule",
        "nkStudySetsSection()", "Continue module", "Create module",
        "route.page==='module-builder'", "studyModuleId:s.studyModuleId||null",
        "s.studyModuleId?'study-module':'practice'",
        'id="nk-custom-study-modules-v1"',
    ]
    missing = [marker for marker in required if marker not in source]
    if missing:
        raise SystemExit(f"Custom Study Modules markers missing after transform: {missing}")
    return source


def main() -> None:
    source = HTML.read_text(encoding="utf-8")
    HTML.write_text(transform(source), encoding="utf-8")
    print("CUSTOM_STUDY_MODULES_OK: persistent stable modules, builder, resume, Home/More, analysis, and unified attempts installed")


if __name__ == "__main__":
    main()
