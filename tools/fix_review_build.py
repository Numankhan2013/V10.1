from pathlib import Path
import re

p = Path('app/src/main/assets/index.html')
s = p.read_text(encoding='utf-8')

for script_id in ('v103-stabilize', 'v103-review-explanation-js', 'v1033-review-hardening'):
    s = re.sub(rf'\n?<script id="{re.escape(script_id)}">.*?</script>\n?', '\n', s, count=1, flags=re.S)
s = s.replace('<!-- V1033_REVIEW_HARDENING -->', '')
s = re.sub(r'\n  function reviewSolutionsGuard\(\)\{.*?\n  reviewSolutionsGuard\(\);\n', '\n', s, count=1, flags=re.S)

old = '<button class="primary-btn v102-review-action" type="button" data-v102-review-cta="1" data-review-test-id="${esc(t.id)}">Review Solutions</button>'
new = '<button class="primary-btn v102-review-action" type="button" data-review-test-id="${esc(t.id)}" onclick="window.QB.reviewTest(this.getAttribute(\'data-review-test-id\'))">Review Solutions</button>'
s = s.replace(old, new, 1)
s = s.replace('data-v102-review-cta="1" data-review-test-id="${esc(t.id)}"', 'data-review-test-id="${esc(t.id)}" onclick="window.QB.reviewTest(this.getAttribute(\'data-review-test-id\'))"', 1)

# Make the review-session constructor compatible with older Android WebViews.
s = s.replace(
    "submitted:Object.fromEntries(t.questionIds.map(id=>[id,Boolean(t.answers?.[id])]))",
    "submitted:t.questionIds.reduce((a,id)=>{a[id]=Boolean(t.answers&&t.answers[id]);return a;},{})",
    1,
)

# Replace the review opener with a minimal, staged implementation. Any failure is
# surfaced with the exact stage so the physical device cannot hide the root cause.
start = s.find('function reviewTest(testId){')
end = s.find('function reviewTestPage(){', start)
if start >= 0 and end > start:
    replacement = '''function reviewTest(testId){
      let stage='lookup';
      try{
        let wanted=String(testId==null?'':testId);
        try{wanted=decodeURIComponent(wanted);}catch(_){stage='lookup-decode';}
        const tests=Array.isArray(state.tests)?state.tests:[];
        const t=tests.find(x=>String(x.id)===wanted || String(x.id)===String(testId));
        if(!t){showToast('That completed test could not be found.','bad');return false;}
        if(!Array.isArray(t.questionIds)||!t.questionIds.length){showToast('This test has no saved questions to review.','bad');return false;}
        stage='session';
        const session=buildReviewSession(t);
        session.questionEnteredAt=Date.now();
        state.activeSession=session;
        stage='save';
        saveState();
        stage='route';
        route={page:'review-test',id:String(t.id)};
        stage='render';
        render();
        stage='history';
        try{history.replaceState(null,'',`#review-test/${encodeURIComponent(String(t.id))}`);}catch(_){location.hash=`#review-test/${encodeURIComponent(String(t.id))}`;}
        return true;
      }catch(e){
        console.error('Review Solutions failed at '+stage,e);
        showToast('Review Solutions failed at '+stage+'.','bad');
        return false;
      }
    }
    '''
    s = s[:start] + replacement + s[end:]

# Review mode should stop cleanly at the final question.
s = s.replace("else if(s.mode==='review'){s.index=0;render();}", "else if(s.mode==='review'){showToast('End of review reached.');render();}", 1)

p.write_text(s, encoding='utf-8')
print('Review runtime hardening applied.')
