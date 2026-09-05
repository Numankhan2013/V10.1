from pathlib import Path
import re

HTML=Path('app/src/main/assets/index.html')
s=HTML.read_text(encoding='utf-8')

# Remove any prior copy so the transform remains deterministic.
s=re.sub(r'<style id="qbank-practice-cleanup-v1">.*?</style>\s*','',s,flags=re.S)

# Give session screens a headerless shell so the question gets the first useful vertical space.
if 'function sessionShell(' not in s:
    needle='  function shell(content, active=\'dashboard\', title=\'QBank\') {'
    if needle not in s: raise SystemExit('shell function not found')
    insert="""  function sessionShell(content, active='dashboard') {\n    return `<main class=\"page fade-in qbank-session-page\">${content}</main>${bottomNav(active)}`;\n  }\n\n"""
    s=s.replace(needle,insert+needle,1)

# Replace the Practice page header/history chrome with the focused question card only.
s=s.replace("    return shell(`\n      <div class=\"page-head\"><div><div class=\"mode-pill\">Practice Mode</div><h1 class=\"page-title\" style=\"margin-top:9px\">${esc(q.chapter)}</h1><div class=\"page-sub\">${esc(q.chapter)} · Question ${q.questionNumber} of ${s.questionIds.length}</div></div><button class=\"ghost-btn\" onclick=\"window.QB.endSession()\">End session</button></div>","    return sessionShell(`\n      <div class=\"practice-focus-head\"><div class=\"q-number\">Question ${q.questionNumber}</div><div class=\"q-actions\">${bookmarkButton(q.id,21)}<button class=\"icon-btn\" aria-label=\"Question Navigator\" onclick=\"window.QB.openQuestionNavigator()\">${navIcon('grid')}</button></div></div>",1)
s=s.replace("<div class=\"q-head\"><div class=\"q-number\">Question ${q.questionNumber}</div><div class=\"q-actions\">${bookmarkButton(q.id,21)}<button class=\"icon-btn\" aria-label=\"More\" onclick=\"window.QB.openQuestionNavigator()\">${navIcon('grid')}</button></div></div><div class=\"crumb\">${esc(q.chapter)}</div>${practiceHistory(q,s)}<div class=\"question-text\">","<div class=\"question-text\">",1)
# The practice header was replaced, but keep the transformation resilient if only the header portion matched.
pstart=s.find('  function practicePage() {')
pend=s.find('\n  function practiceActionBar',pstart)
if pstart<0 or pend<0: raise SystemExit('practicePage boundaries not found')
practice=s[pstart:pend]
practice=re.sub(r'<div class="crumb">\$\{esc\(q\.chapter\)\}</div>', '', practice, count=1)
practice=re.sub(r'\$\{practiceHistory\(q,s\)\}', '', practice, count=1)
s=s[:pstart]+practice+s[pend:]
s=s.replace("    `,'topics','Practice') + practiceActionBar(s, q, selected, submitted);","    `,'topics') + practiceActionBar(s, q, selected, submitted);",1)

# Make the grid the sole location for Practice session termination.
old="    const submit=exam?'<button type=\"button\" class=\"primary-btn qb-nav-submit\" onclick=\"window.QB.submitExam(false)\">Submit Test</button>':'';"
new="    const submit=exam?'<button type=\"button\" class=\"primary-btn qb-nav-submit\" onclick=\"window.QB.submitExam(false)\">Submit Test</button>':s.mode==='practice'?'<button type=\"button\" class=\"primary-btn qb-nav-submit\" onclick=\"window.QB.endSession()\">End session</button>':'';"
if old not in s: raise SystemExit('navigator submit line not found')
s=s.replace(old,new,1)

css=r'''<style id="qbank-practice-cleanup-v1">
/* V10.3.10 — focused Practice screen: question first, session controls in navigator. */
.qbank-session-page{padding-top:12px!important}
.practice-focus-head{display:flex;align-items:center;justify-content:space-between;max-width:760px;margin:0 auto 8px;padding:0 2px}
.practice-focus-head .q-number{font-size:13px;font-weight:800;color:var(--text)}
.practice-focus-head .q-actions{display:flex;align-items:center;gap:8px}
.qbank-session-page .question-shell{margin-top:0!important}
.qbank-session-page .question-card{margin-top:0!important}
.qbank-session-page .question-card>.q-head{display:none!important}
.qbank-session-page .history-strip{display:none!important}
.qbank-session-page .mode-pill,.qbank-session-page>.page-head,.qbank-session-page .page-sub{display:none!important}
/* Once an answer is submitted, the radio slot has no semantic purpose. Remove it entirely. */
.qbank-session-page .question-card .option.correct .radio,
.qbank-session-page .question-card .option.wrong .radio{display:none!important}
.qbank-session-page .question-card .option.correct .option-letter,
.qbank-session-page .question-card .option.wrong .option-letter{margin-left:0!important}
.qbank-session-page .question-card .option.correct,
.qbank-session-page .question-card .option.wrong{grid-template-columns:auto 1fr!important}
.qbank-session-page .question-card .option.correct .option-text,
.qbank-session-page .question-card .option.wrong .option-text{grid-column:auto!important}
.qb-nav-submit{width:100%;margin-top:10px;min-height:46px}
@media(max-width:640px){
  .qbank-session-page{padding-top:9px!important}
  .practice-focus-head{margin-bottom:6px}
}
</style>'''
if '</head>' not in s: raise SystemExit('</head> missing')
s=s.replace('</head>',css+'\n</head>',1)
HTML.write_text(s,encoding='utf-8')
print('V10.3.10 practice cleanup applied.')