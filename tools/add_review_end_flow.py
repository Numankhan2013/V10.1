from pathlib import Path
import re

HTML = Path('app/src/main/assets/index.html')
s = HTML.read_text(encoding='utf-8')

# Review Solutions needs an explicit, non-destructive exit. Keep the existing
# test/practice navigator behavior untouched and add the control only for the
# review session mode.
if 'function endReview()' not in s:
    marker = '  function nextQ(){'
    helper = '''  function endReview(){
    const s=state.activeSession;
    if(!s || s.mode!=='review') return;
    state.activeSession=null;
    saveState();
    closeQuestionNavigator();
    navigate('tests');
  }
'''
    if marker not in s:
        raise SystemExit('Could not locate nextQ() for Review Solutions end-flow insertion.')
    s = s.replace(marker, helper + marker, 1)

old_branch = "else if(s.mode==='review'){s.index=0;render();}"
new_branch = "else if(s.mode==='review'){openQuestionNavigator();}"
if old_branch in s:
    s = s.replace(old_branch, new_branch, 1)
elif new_branch not in s:
    raise SystemExit('Could not locate Review Solutions final-question branch.')

old_submit = ":s.mode==='practice'?'<button type=\"button\" class=\"primary-btn qb-nav-submit\" onclick=\"window.QB.endSession()\">End session</button>':'';"
new_submit = ":s.mode==='practice'?'<button type=\"button\" class=\"primary-btn qb-nav-submit\" onclick=\"window.QB.endSession()\">End session</button>':s.mode==='review'?'<button type=\"button\" class=\"primary-btn qb-nav-submit\" onclick=\"window.QB.endReview()\">End Review</button>':'';"
if old_submit in s:
    s = s.replace(old_submit, new_submit, 1)
elif 'window.QB.endReview()' not in s:
    raise SystemExit('Could not add End Review action to the existing Question Navigator.')

# Expose the lexical helper through the existing public QB object without
# replacing any existing navigator/session APIs.
if 'endReview:endReview' not in s:
    m = re.search(r'window\.QB=\{([^\n]+)\};', s)
    if not m:
        raise SystemExit('Could not locate canonical window.QB object assignment.')
    body = m.group(1)
    body += ',endReview:endReview'
    s = s[:m.start(1)] + body + s[m.end(1):]

HTML.write_text(s, encoding='utf-8')
print('Review Solutions end-flow installed: final Next opens the existing navigator, and review navigator exposes End Review.')
