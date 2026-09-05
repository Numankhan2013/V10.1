from pathlib import Path
import re

INDEX = Path('app/src/main/assets/index.html')
text = INDEX.read_text(encoding='utf-8')

# Keep the legacy setSubject compatibility API intact, but add one deterministic
# path for the Home/Topics subject library: select a subject and open its Topics
# view without the legacy modal/flash layer.
if 'function openSubjectTopics(name)' not in text:
    pattern = re.compile(r"function setSubject\(name\)\{.*?\}")
    m = pattern.search(text)
    if not m:
        raise SystemExit('setSubject function target not found')
    set_fn = m.group(0)
    # The generated function contains no nested braces, so this exact replacement
    # is safe for the current V4 generator.
    new = set_fn + "\n  function openSubjectTopics(name){ if(!SUBJECT_BY_NAME[name]) return; applySubject(name); searchTerm=''; topicFilter='all'; if(route && route.page==='topics'){ render(); requestAnimationFrame(() => window.scrollTo(0,0)); } else { navigate('topics'); } }"
    text = text[:m.start()] + new + text[m.end():]

# Export the deterministic subject-opening API.
if 'openSubjectTopics,toggleMenu' not in text:
    old = "window.QB={getState:()=>state,nav:navigate,setSubject,toggleMenu,notify,openQuestionNavigator"
    new = "window.QB={getState:()=>state,nav:navigate,setSubject,openSubjectTopics,toggleMenu,notify,openQuestionNavigator"
    if old not in text:
        raise SystemExit('QB export target not found')
    text = text.replace(old, new, 1)

# Home V4 subject rows must open Topics for the selected subject.
if "window.QB.openSubjectTopics('${esc(x.subject)}')" not in text:
    old = "onclick=\"window.QB.setSubject('${esc(x.subject)}')\""
    new = "onclick=\"window.QB.openSubjectTopics('${esc(x.subject)}')\""
    if old not in text:
        raise SystemExit('Home subject click target not found')
    text = text.replace(old, new, 1)

# Replace the Topics subject picker with the same direct navigation path. This
# deliberately removes data-v102-subject-card from these buttons so the legacy
# capture-phase modal cannot intercept them and produce the reported flash.
if 'class="v102-subject-card' in text and "onclick=\"window.QB.openSubjectTopics('${esc(x.subject)}')\"" not in text[text.find('function subjectPickerMarkup'):text.find('function subjectPickerMarkup')+2500]:
    start = text.find('function subjectPickerMarkup(){')
    if start < 0:
        raise SystemExit('subjectPickerMarkup target not found')
    end = text.find('function setSubject(name)', start)
    if end < 0:
        raise SystemExit('subjectPickerMarkup end not found')
    replacement = '''function subjectPickerMarkup(){
      return `<section class="v102-subject-hub" aria-labelledby="v102-subject-title"><div class="v102-section-head"><div><div class="v102-eyebrow">Study library</div><h2 id="v102-subject-title">Choose a subject</h2></div><span>${fmtNum(SUBJECTS.length)} subjects</span></div><div class="v102-subject-grid">${SUBJECTS.map(x=>`<button type="button" class="v102-subject-card ${x.subject===activeSubject?'is-active':''}" onclick="window.QB.openSubjectTopics('${esc(x.subject)}')" aria-pressed="${x.subject===activeSubject?'true':'false'}"><span class="v102-subject-mark">${subjectIcon(x.subject,46)}</span><span class="v102-subject-copy"><strong>${esc(x.subject)}</strong><small>${fmtNum((x.topics||[]).length || (x.chapters||[]).length || 0)} topics · ${fmtNum((x.questions||[]).length)} questions</small></span><span class="v102-subject-arrow" aria-hidden="true">›</span></button>`).join('')}</div><p class="v102-subject-hint">Tap a subject to open its topics, then jump straight into a chapter.</p></section>`;
    }
    '''
    text = text[:start] + replacement + text[end:]

# Scope the existing streak component to Home. It remains available everywhere
# in code, but is now rendered only by dashboard(), so it cannot leak into
# Topics, Practice, or Question screens.
if '${streakMarkup()}' not in text:
    needle = '        </header>\n        <section class="nk-home-v4-today">'
    replacement = '        </header>\n        ${streakMarkup()}\n        <section class="nk-home-v4-today">'
    if needle not in text:
        raise SystemExit('Home streak insertion target not found')
    text = text.replace(needle, replacement, 1)

# Route changes begin at the top; retain the WebView-safe scroll form.
if 'requestAnimationFrame(() => window.scrollTo(0,0))' not in text:
    old = "window.addEventListener('hashchange', () => { route = parseHash(); render(); });"
    new = "window.addEventListener('hashchange', () => { route = parseHash(); render(); requestAnimationFrame(() => window.scrollTo(0,0)); });"
    if old not in text:
        raise SystemExit('hashchange target not found')
    text = text.replace(old, new, 1)

# Normalize Home subject counts when the source stores questions/topics as arrays.
if 'subjectQuestions=Array.isArray' not in text:
    old = "const q=QUESTIONS.filter(v=>v.subject===x.subject), done=q.filter(v=>state.answers&&state.answers[v.id]).length, pct=q.length?Math.round(done/q.length*100):0;"
    new = "const q=QUESTIONS.filter(v=>v.subject===x.subject), done=q.filter(v=>state.answers&&state.answers[v.id]).length, pct=q.length?Math.round(done/q.length*100):0, subjectQuestions=Array.isArray(x.questions)?x.questions.length:(Number(x.questions)||q.length), subjectTopics=Array.isArray(x.topics)?x.topics.length:(Array.isArray(x.chapters)?x.chapters.length:(Number(x.topics)||0));"
    if old not in text:
        raise SystemExit('Home V4 subject calculation target not found')
    text = text.replace(old, new, 1)
    text = text.replace("${fmtNum(x.questions||q.length)} questions · ${fmtNum(x.topics||0)} topics", "${fmtNum(subjectQuestions)} questions · ${fmtNum(subjectTopics)} topics", 1)

# Remove the old global streak injector. The real streak card is now explicitly
# composed into dashboard(), not globally injected into every route.
if 'id="v102-streak-layer-script"' in text:
    pattern = re.compile(r'\n<style id="v102-streak-layer">.*?</style>\n<script id="v102-streak-layer-script">.*?</script>\n', re.S)
    text, n = pattern.subn('\n', text, count=1)
    if n != 1:
        raise SystemExit('legacy streak layer target not found')

marker = '<!-- NK_HOME_V5_FIXES -->'
if marker not in text:
    text = text.replace('</head>', marker + '</head>', 1)

INDEX.write_text(text, encoding='utf-8')
print('Applied Home subject/navigation V6: direct subject-to-topics routing, no legacy modal interception, Home-only streak, route scroll reset, and NaN-safe counts.')