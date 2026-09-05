from pathlib import Path
import re

INDEX = Path('app/src/main/assets/index.html')

text = INDEX.read_text(encoding='utf-8')

# Home subject selection must open the subject's Topics view, not merely change
# activeSubject while leaving the user on Home. Keep setSubject() as a safe
# compatibility API for older code, and introduce a deterministic subject-open
# path used by the new Home/Topics UI.
old = "function setSubject(name){ if(!SUBJECT_BY_NAME[name]) return; applySubject(name); searchTerm=''; topicFilter='all'; if(route && route.page==='dashboard'){ render(); window.scrollTo(0,0); } else { navigate('dashboard'); } }"
new = "function setSubject(name){ if(!SUBJECT_BY_NAME[name]) return; applySubject(name); searchTerm=''; topicFilter='all'; if(route && route.page==='dashboard'){ render(); window.scrollTo(0,0); } else { navigate('dashboard'); } }\n  function openSubjectTopics(name){ if(!SUBJECT_BY_NAME[name]) return; applySubject(name); searchTerm=''; topicFilter='all'; if(route && route.page==='topics'){ render(); requestAnimationFrame(() => window.scrollTo(0,0)); } else { navigate('topics'); } }"
if old not in text:
    raise SystemExit('setSubject target not found')
text = text.replace(old, new, 1)

# Export the deterministic subject-opening API alongside the existing API.
old = "window.QB={getState:()=>state,nav:navigate,setSubject,toggleMenu,notify,openQuestionNavigator"
new = "window.QB={getState:()=>state,nav:navigate,setSubject,openSubjectTopics,toggleMenu,notify,openQuestionNavigator"
if old not in text:
    raise SystemExit('QB export target not found')
text = text.replace(old, new, 1)

# Home V4 subject rows should open the Topics view for the chosen subject.
old = "onclick=\"window.QB.setSubject('${esc(x.subject)}')\""
new = "onclick=\"window.QB.openSubjectTopics('${esc(x.subject)}')\""
if old not in text:
    raise SystemExit('Home subject click target not found')
text = text.replace(old, new, 1)

# Replace the legacy subject-picker markup used by Topics with the same direct,
# no-modal navigation path. The old delegated v102 modal caused a visible flash
# and a second interaction layer before the topic list could be reached.
old_start = "function subjectPickerMarkup(){"
start = text.find(old_start)
if start < 0:
    raise SystemExit('subjectPickerMarkup target not found')
end = text.find("    function setSubject(name)", start)
if end < 0:
    raise SystemExit('subjectPickerMarkup end not found')
replacement = '''function subjectPickerMarkup(){
      return `<section class="v102-subject-hub" aria-labelledby="v102-subject-title"><div class="v102-section-head"><div><div class="v102-eyebrow">Study library</div><h2 id="v102-subject-title">Choose a subject</h2></div><span>${fmtNum(SUBJECTS.length)} subjects</span></div><div class="v102-subject-grid">${SUBJECTS.map(x=>`<button type="button" class="v102-subject-card ${x.subject===activeSubject?'is-active':''}" onclick="window.QB.openSubjectTopics('${esc(x.subject)}')" aria-pressed="${x.subject===activeSubject?'true':'false'}"><span class="v102-subject-mark">${subjectIcon(x.subject,46)}</span><span class="v102-subject-copy"><strong>${esc(x.subject)}</strong><small>${fmtNum((x.topics||[]).length || (x.chapters||[]).length || 0)} topics · ${fmtNum((x.questions||[]).length)} questions</small></span><span class="v102-subject-arrow" aria-hidden="true">›</span></button>`).join('')}</div><p class="v102-subject-hint">Tap a subject to open its topics, then jump straight into a chapter.</p></section>`;
    }
'''
text = text[:start] + replacement + text[end:]

# Scope the study streak to Home by putting the existing streak component into
# the dashboard composition. The old global injector was removed because it
# leaked into Topics/Practice/Question pages; the component itself is useful
# and should remain visible on Home.
needle = "        </header>\n        <section class=\"nk-home-v4-today\">"
replacement = "        </header>\n        ${streakMarkup()}\n        <section class=\"nk-home-v4-today\">"
if needle not in text:
    raise SystemExit('Home streak insertion target not found')
text = text.replace(needle, replacement, 1)

# Every hash route transition starts at the top. Keep the WebView-safe form.
old = "window.addEventListener('hashchange', () => { route = parseHash(); render(); requestAnimationFrame(() => window.scrollTo(0,0)); });"
new = "window.addEventListener('hashchange', () => { route = parseHash(); render(); requestAnimationFrame(() => window.scrollTo(0,0)); });"
if old not in text:
    raise SystemExit('hashchange target not found')

# Home V4 data labels were reading array-valued questions/topics as numbers,
# producing NaN. Normalize both array and numeric representations.
old = "const q=QUESTIONS.filter(v=>v.subject===x.subject), done=q.filter(v=>state.answers&&state.answers[v.id]).length, pct=q.length?Math.round(done/q.length*100):0;"
new = "const q=QUESTIONS.filter(v=>v.subject===x.subject), done=q.filter(v=>state.answers&&state.answers[v.id]).length, pct=q.length?Math.round(done/q.length*100):0, subjectQuestions=Array.isArray(x.questions)?x.questions.length:(Number(x.questions)||q.length), subjectTopics=Array.isArray(x.topics)?x.topics.length:(Array.isArray(x.chapters)?x.chapters.length:(Number(x.topics)||0));"
if old not in text:
    raise SystemExit('Home V4 subject calculation target not found')
text = text.replace(old, new, 1)
text = text.replace("${fmtNum(x.questions||q.length)} questions · ${fmtNum(x.topics||0)} topics", "${fmtNum(subjectQuestions)} questions · ${fmtNum(subjectTopics)} topics", 1)

# Remove the legacy global streak injector. The streak component is now rendered
# explicitly by dashboard(), so it cannot seep into other routes.
pattern = re.compile(r'\n<style id="v102-streak-layer">.*?</style>\n<script id="v102-streak-layer-script">.*?</script>\n', re.S)
text, n = pattern.subn('\n', text, count=1)
if n != 1:
    raise SystemExit('legacy streak layer target not found')

marker = '<!-- NK_HOME_V5_FIXES -->'
if marker not in text:
    text = text.replace('</head>', marker + '</head>', 1)

INDEX.write_text(text, encoding='utf-8')
print('Applied Home V6 functional fixes: direct subject->topics navigation, no-modal topic switching, scoped Home streak, scroll reset, NaN labels, legacy streak isolation.')