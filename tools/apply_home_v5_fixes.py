from pathlib import Path
import re

INDEX = Path('app/src/main/assets/index.html')

text = INDEX.read_text(encoding='utf-8')

# Subject selection on the Home screen was calling setSubject(), which navigated
# to the same hash (#dashboard). Since the hash did not change, hashchange did
# not fire and the Home DOM never re-rendered. Render immediately when already
# on Home; otherwise preserve normal navigation.
old = "function setSubject(name){ if(!SUBJECT_BY_NAME[name]) return; applySubject(name); searchTerm=''; topicFilter='all'; navigate('dashboard'); }"
new = "function setSubject(name){ if(!SUBJECT_BY_NAME[name]) return; applySubject(name); searchTerm=''; topicFilter='all'; if(route && route.page==='dashboard'){ render(); window.scrollTo(0,0); } else { navigate('dashboard'); } }"
if old not in text:
    raise SystemExit('setSubject target not found')
text = text.replace(old, new, 1)

# Every route transition should begin at the top. This applies to Home quick
# access, bottom navigation, topic/test/insight pages, and other hash routes.
old = "window.addEventListener('hashchange', () => { route = parseHash(); render(); });"
new = "window.addEventListener('hashchange', () => { route = parseHash(); render(); requestAnimationFrame(() => window.scrollTo({top:0,left:0,behavior:'instant'})); });"
if old not in text:
    raise SystemExit('hashchange target not found')
text = text.replace(old, new, 1)

# Home V4 data labels were reading array-valued questions/topics as numbers,
# producing NaN. Normalize both array and numeric representations.
old = "const q=QUESTIONS.filter(v=>v.subject===x.subject), done=q.filter(v=>state.answers&&state.answers[v.id]).length, pct=q.length?Math.round(done/q.length*100):0;"
new = "const q=QUESTIONS.filter(v=>v.subject===x.subject), done=q.filter(v=>state.answers&&state.answers[v.id]).length, pct=q.length?Math.round(done/q.length*100):0, subjectQuestions=Array.isArray(x.questions)?x.questions.length:(Number(x.questions)||q.length), subjectTopics=Array.isArray(x.topics)?x.topics.length:(Array.isArray(x.chapters)?x.chapters.length:(Number(x.topics)||0));"
if old not in text:
    raise SystemExit('Home V4 subject calculation target not found')
text = text.replace(old, new, 1)
text = text.replace("${fmtNum(x.questions||q.length)} questions · ${fmtNum(x.topics||0)} topics", "${fmtNum(subjectQuestions)} questions · ${fmtNum(subjectTopics)} topics", 1)

# The legacy V10.2 streak layer was designed as a global injected card and can
# attach itself to arbitrary pages. V4 owns Home composition now, so remove the
# legacy injector entirely rather than hiding symptoms with page-specific CSS.
pattern = re.compile(r'\n<style id="v102-streak-layer">.*?</style>\n<script id="v102-streak-layer-script">.*?</script>\n', re.S)
text, n = pattern.subn('\n', text, count=1)
if n != 1:
    raise SystemExit('legacy streak layer target not found')

# Add a small regression marker so the workflow can prove these fixes reached
# the generated app.
marker = '<!-- NK_HOME_V5_FIXES -->'
if marker not in text:
    text = text.replace('</head>', marker + '</head>', 1)

INDEX.write_text(text, encoding='utf-8')
print('Applied Home V5 functional fixes: subject selection, scroll reset, NaN labels, legacy streak isolation.')
