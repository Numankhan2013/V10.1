from pathlib import Path
import re

HTML = Path('app/src/main/assets/index.html')
s = HTML.read_text(encoding='utf-8')

# Remove every previous canonical CBT runtime layer. The normal app renderer is
# the sole owner of the Review Solutions screen; this layer only enters it.
s = re.sub(r'<script id="cbt-canonical-review">.*?</script>\s*', '', s, flags=re.S)
s = re.sub(r'<script id="cbt-final-lock-v3">.*?</script>\s*', '', s, flags=re.S)
s = re.sub(r'<script id="cbt-final-lock-v2">.*?</script>\s*', '', s, flags=re.S)

# Normalize all known Review Solutions CTA forms to one entry point.
s = s.replace("onclick=\"window.QB.reviewTest(this.getAttribute('data-review-test-id'))\"", "onclick=\"return window.__QB_OPEN_REVIEW(this.getAttribute('data-review-test-id'))\"")
s = s.replace("onclick=\"return window.__QB_OPEN_REVIEW(this.getAttribute('data-review-test-id'))\"", "onclick=\"return window.__QB_OPEN_REVIEW(this.getAttribute('data-review-test-id'))\"")

lock = r'''<script id="cbt-canonical-review">
(function(){
  'use strict';
  function getState(){
    try{if(window.QB&&typeof window.QB.getState==='function'){var x=window.QB.getState();if(x)return x;}}catch(e){}
    try{return JSON.parse(localStorage.getItem('qbank_state_v1')||'{}');}catch(e){return {};}
  }
  function persist(st,s){st.activeSession=s;localStorage.setItem('qbank_state_v1',JSON.stringify(st));}
  function openReview(testId){
    var st=getState(),wanted;
    try{wanted=decodeURIComponent(String(testId||''));}catch(e){wanted=String(testId||'');}
    var tests=Array.isArray(st.tests)?st.tests:[];
    var t=tests.find(function(x){return String(x.id)===wanted||String(x.id)===String(testId);});
    if(!t||!Array.isArray(t.questionIds)||!t.questionIds.length){console.error('Canonical CBT Review: test not found',wanted);return false;}
    var s={id:'review_'+String(t.id),mode:'review',sourceTestId:String(t.id),title:'Review · '+String(t.title||'Completed Test'),questionIds:t.questionIds.slice(),index:0,answers:Object.assign({},t.answers||{}),questionTimes:Object.assign({},t.questionTimes||{})};
    persist(st,s);
    try{window.route={page:'review-test',id:String(t.id)};}catch(e){}
    try{history.replaceState(null,'','#review-test/'+encodeURIComponent(String(t.id)));}catch(e){location.hash='#review-test/'+encodeURIComponent(String(t.id));}
    try{if(typeof window.render==='function')window.render();else location.hash='#review-test/'+encodeURIComponent(String(t.id));}catch(e){console.error('Canonical CBT Review render failed',e);return false;}
    return false;
  }
  window.__QB_OPEN_REVIEW=openReview;
  window.QB=window.QB||{};
  window.QB.reviewTest=openReview;
})();
</script>'''
s=s.replace('</body>',lock+'\n</body>',1)
HTML.write_text(s,encoding='utf-8')
print('Canonical Review Solutions entry point installed; normal QBank question renderer remains authoritative.')
