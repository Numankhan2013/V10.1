from pathlib import Path
import re

INDEX = Path('app/src/main/assets/index.html')
text = INDEX.read_text(encoding='utf-8')


def replace_function(source, signature, replacement):
    """Replace one JS function using balanced-brace scanning."""
    start = source.find(signature)
    if start < 0:
        raise SystemExit(f'{signature} target not found')
    brace = source.find('{', start)
    if brace < 0:
        raise SystemExit(f'{signature} opening brace not found')
    depth = 0
    in_str = None
    escape = False
    i = brace
    while i < len(source):
        ch = source[i]
        if in_str:
            if escape:
                escape = False
            elif ch == '\\':
                escape = True
            elif ch == in_str:
                in_str = None
        else:
            if ch in ('"', "'", '`'):
                in_str = ch
            elif ch == '{':
                depth += 1
            elif ch == '}':
                depth -= 1
                if depth == 0:
                    return source[:start] + replacement + source[i + 1:]
        i += 1
    raise SystemExit(f'{signature} closing brace not found')


# Preserve setSubject() for compatibility, and add a separate direct route for
# the actual subject library. This avoids the old subject modal and makes a tap
# on a Home/Topics subject deterministically land in Topics for that subject.
if 'function openSubjectTopics(name)' not in text:
    set_replacement = """function setSubject(name){
    if(!SUBJECT_BY_NAME[name]) return;
    applySubject(name);
    searchTerm='';
    topicFilter='all';
    if(route && route.page==='dashboard'){
      render();
      window.scrollTo(0,0);
    } else {
      navigate('dashboard');
    }
  }
  function openSubjectTopics(name){
    if(!SUBJECT_BY_NAME[name]) return;
    applySubject(name);
    searchTerm='';
    topicFilter='all';
    if(route && route.page==='topics'){
      render();
      requestAnimationFrame(() => window.scrollTo(0,0));
    } else {
      navigate('topics');
    }
  }"""
    text = replace_function(text, 'function setSubject(name)', set_replacement)

# Export the new route function.
if 'setSubject,openSubjectTopics,toggleMenu' not in text:
    old = "window.QB={getState:()=>state,nav:navigate,setSubject,toggleMenu,notify,openQuestionNavigator"
    new = "window.QB={getState:()=>state,nav:navigate,setSubject,openSubjectTopics,toggleMenu,notify,openQuestionNavigator"
    if old not in text:
        raise SystemExit('QB export target not found')
    text = text.replace(old, new, 1)

# Home V4 subject rows should open Topics directly.
text = text.replace(
    "onclick=\"window.QB.setSubject('${esc(x.subject)}')\"",
    "onclick=\"window.QB.openSubjectTopics('${esc(x.subject)}')\"",
    1,
)

# Topics subject picker: remove data-v102-subject-card so the legacy capture
# listener cannot open its modal. Use the same direct subject->Topics route.
start = text.find('function subjectPickerMarkup(){')
if start < 0:
    raise SystemExit('subjectPickerMarkup target not found')
end = text.find('function setSubject(name)', start)
if end < 0:
    raise SystemExit('subjectPickerMarkup end not found')
old_picker = text[start:end]
new_picker = old_picker.replace(' data-v102-subject-card="1"', '')
new_picker = new_picker.replace(
    'onclick="window.QB.v102SelectSubject(\'${esc(x.subject)}\')"',
    'onclick="window.QB.openSubjectTopics(\'${esc(x.subject)}\')"',
)
# Current legacy picker is data-attribute based rather than onclick based.
new_picker = new_picker.replace(
    ' data-subject="${encodeURIComponent(x.subject)}"',
    '',
)
if 'openSubjectTopics' not in new_picker:
    new_picker = re.sub(
        r'<button type="button" class="v102-subject-card ([^"]*)"([^>]*)>',
        r'<button type="button" class="v102-subject-card \1" onclick="window.QB.openSubjectTopics(\'${esc(x.subject)}\')"\2>',
        new_picker,
        count=1,
    )
if 'openSubjectTopics' not in new_picker:
    raise SystemExit('Topics subject picker replacement did not produce direct route')
text = text[:start] + new_picker + text[end:]

# Scope the existing streak component to Home. It stays implemented, but is
# composed only inside dashboard(), preventing leakage into other routes.
if '${streakMarkup()}' not in text:
    needle = '        </header>\n        <section class="nk-home-v4-today">'
    replacement = '        </header>\n        ${streakMarkup()}\n        <section class="nk-home-v4-today">'
    if needle not in text:
        raise SystemExit('Home streak insertion target not found')
    text = text.replace(needle, replacement, 1)

# Every hash route transition begins at the top. Keep the simple WebView-safe
# form rather than ScrollToOptions behavior enums.
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

# Delete only the old global streak injector. The streak card itself is now
# explicitly rendered by dashboard().
if 'id="v102-streak-layer-script"' in text:
    pattern = re.compile(r'\n<style id="v102-streak-layer">.*?</style>\n<script id="v102-streak-layer-script">.*?</script>\n', re.S)
    text, n = pattern.subn('\n', text, count=1)
    if n != 1:
        raise SystemExit('legacy streak layer target not found')

marker = '<!-- NK_HOME_V5_FIXES -->'
if marker not in text:
    text = text.replace('</head>', marker + '</head>', 1)

INDEX.write_text(text, encoding='utf-8')
print('Applied Home V6: direct subject->Topics routing, legacy subject-modal bypass, Home-only streak, route scroll reset, and NaN-safe counts.')