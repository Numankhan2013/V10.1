from pathlib import Path
import re

p = Path('app/src/main/assets/index.html')
s = p.read_text(encoding='utf-8')

marker = 'function reviewTestPage()'
start = s.find(marker)
end = s.find('function closeQuestionNavigator()', start)
if start < 0 or end < 0:
    raise SystemExit('Could not locate Review Solutions renderer boundaries; refusing ambiguous UI patch.')
seg = s[start:end]

seg, _ = re.subn(r'\n\s*<div class="page-head">.*?<button class="ghost-btn" onclick="window\.QB\.nav\(\'tests\'\)"[^>]*>Back to Tests</button></div>', '', seg, count=1, flags=re.S)
seg, n = re.subn(r'\breturn shell\(`', 'return sessionShell(`', seg, count=1)
if n != 1: raise SystemExit('Review Solutions session shell could not be established.')
head_pat = re.compile(r'<section class="card question-card"><div class="q-head">.*?</div><div class="crumb">', re.S)
head_repl = ('<div class="practice-focus-head"><div class="q-number">Question ${q.questionNumber} of ${s.questionIds.length}</div><div class="q-actions">'
             '${bookmarkButton(q.id,21)}<button class="icon-btn" id="cr-grid" aria-label="Question Navigator" title="Question Navigator" onclick="window.QB.openQuestionNavigator()">${navIcon(\'grid\')}</button>'
             '</div></div><div class="question-shell"><section class="card question-card"><div class="crumb">')
seg, n = head_pat.subn(head_repl, seg, count=1)
if n != 1: raise SystemExit('Review Solutions question header could not be replaced.')
explain_pat = re.compile(r'\$\{q\.explanation\?`<div class="label">Source explanation</div><div class="feedback-body">.*?</div>`:\'\'}', re.S)
explain_repl = '${q.explanation?`<div class="label">Source explanation</div><div class="feedback-body source-explanation">${renderExplanationText(q.explanation,q)}</div>`:\'\'}'
seg, n = explain_pat.subn(explain_repl, seg, count=1)
if n != 1: raise SystemExit('Review Solutions explanation block could not be replaced.')
if 'renderExplanationText(q.explanation,q)' not in seg: raise SystemExit('Review Solutions source-PDF explanation renderer is missing.')
seg = seg.replace('</div></section>\n    `', '</section></div>\n    `', 1)
footer = '<div class="q-footer"><button class="ghost-btn" onclick="window.QB.prevQ()">Previous</button><button class="primary-btn" onclick="window.QB.nextQ()">Next ${navIcon(\'chevron\',15)}</button></div>'
if 'nk-review-fixed-bar' not in seg:
    if footer not in seg: raise SystemExit('Could not locate Review Solutions footer; refusing ambiguous patch.')
    inner = footer[len('<div class="q-footer">'):-len('</div>')]
    seg = seg.replace(footer, '<div class="nk-review-footer-spacer"></div><div class="nk-review-fixed-bar"><div class="nk-review-fixed-bar-inner">' + inner + '</div></div>', 1)
s = s[:start] + seg + s[end:]

# Review boundary: final Next opens the shared navigator; End Review closes it
# before returning directly to the exact originating Test/Practice Analysis.
if 'function endReview()' not in s:
    next_marker = '  function nextQ(){'
    helper = '''  function endReview(){
    const s=state.activeSession;
    if(!s || s.mode!=='review') return;
    const sourceTestId=s.sourceTestId;
    closeQuestionNavigator();
    state.activeSession=null;
    saveState();
    if(sourceTestId && state.tests.some(t=>String(t.id)===String(sourceTestId))) navigate('result',String(sourceTestId));
    else navigate('tests');
  }
'''
    if next_marker not in s: raise SystemExit('Could not locate nextQ() for Review Solutions end-flow insertion.')
    s = s.replace(next_marker, helper + next_marker, 1)
old_branch = "else if(s.mode==='review'){s.index=0;render();}"
new_branch = "else if(s.mode==='review'){closeQuestionNavigator();openQuestionNavigator();}"
if old_branch in s: s=s.replace(old_branch,new_branch,1)
elif new_branch not in s: raise SystemExit('Could not locate Review Solutions final-question branch.')
old_submit = ":s.mode==='practice'?'<button type=\"button\" class=\"primary-btn qb-nav-submit\" onclick=\"window.QB.endSession()\">End session</button>':'';"
new_submit = ":s.mode==='practice'?'<button type=\"button\" class=\"primary-btn qb-nav-submit\" onclick=\"window.QB.endSession()\">End session</button>':s.mode==='review'?'<button type=\"button\" class=\"primary-btn qb-nav-submit\" onclick=\"window.QB.endReview()\">End Review</button>':'';"
if old_submit in s: s=s.replace(old_submit,new_submit,1)
elif 'window.QB.endReview()' not in s: raise SystemExit('Could not add End Review action to the existing Question Navigator.')
if 'endReview:endReview' not in s:
    m=re.search(r'window\.QB=\{([^\n]+)\};',s)
    if not m: raise SystemExit('Could not locate canonical window.QB object assignment.')
    body=m.group(1)+',endReview:endReview'
    s=s[:m.start(1)]+body+s[m.end(1):]
if 'id="nk-review-solution-grid-style"' not in s: s=s.replace('</head>','<style id="nk-review-solution-grid-style"></style>\n</head>',1)
p.write_text(s,encoding='utf-8')
print('Review Solutions hardened: source-PDF explanations + bookmark/grid + fixed Previous/Next + End Review + automatic navigator at final question + clean return to originating analysis.')
