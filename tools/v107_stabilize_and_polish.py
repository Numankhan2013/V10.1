from pathlib import Path
import re

HTML = Path('app/src/main/assets/index.html')
s = HTML.read_text(encoding='utf-8')

# Stop the V10.5 observer loop: the old code inserted the hint beside .option-list,
# then searched inside .option-list for it, so every mutation inserted another hint.
s = s.replace(
    "if(list&&!list.querySelector('.v105-option-hint')){var h=document.createElement('p');h.className='v105-option-hint';h.textContent='Select the best answer';list.parentNode.insertBefore(h,list)}",
    "if(list&&!list.parentNode.querySelector('.v105-option-hint')){var h=document.createElement('p');h.className='v105-option-hint';h.textContent='Select the best answer';list.parentNode.insertBefore(h,list)}"
)

# Subject cards belong on Home only. The old V10.5 tick() called subjectCards()
# on every route, which injected Biochemistry/Physiology/Anatomy into question/topic pages.
s = s.replace(
    "function tick(){try{if(location.hash==='#dashboard'||location.hash===''||location.hash==='#')dashboard();}catch(e){}subjectCards();questionPolish()}",
    "function tick(){try{var home=location.hash==='#dashboard'||location.hash===''||location.hash==='#';if(home){dashboard();subjectCards();}}catch(e){}questionPolish()}"
)

# Expose the existing proven practice engine to the native shell. It starts the
# same mixed-practice session used by the original working QBank rather than
# navigating to a non-existent landing route.
bridge = r'''<script id="v107-practice-bridge">
(function(){
  window.QB=window.QB||{};
  if(typeof window.QB.startPractice!=='function' && typeof window.startAllPractice==='function'){
    window.QB.startPractice=function(){return window.startAllPractice();};
  }
  if(typeof window.QB.openSubject!=='function' && typeof window.navigate==='function'){
    window.QB.openSubject=function(subject){
      var s=String(subject||'').toLowerCase();
      if(s==='biochemistry') return window.navigate('dashboard');
      if(s==='physiology') return window.navigate('dashboard');
      if(s==='anatomy') return window.navigate('dashboard');
    };
  }
})();
</script>'''
if 'id="v107-practice-bridge"' not in s:
    s = s.replace('</body>', bridge + '\n</body>', 1)

# Native-shell-friendly route marker. The Android shell reads this via the page
# hash and hides the bar over full-screen question/review screens.
shell_hint = r'''<script id="v107-shell-route-hint">
(function(){
  function notify(){try{document.documentElement.setAttribute('data-qb-route',(location.hash||'#dashboard').slice(1));}catch(e){}}
  window.addEventListener('hashchange',notify); notify();
})();
</script>'''
if 'id="v107-shell-route-hint"' not in s:
    s = s.replace('</body>', shell_hint + '\n</body>', 1)

# Prevent duplicate V10.4/V10.5 command overlays from accumulating when the
# WebView re-renders the dashboard. The actual dashboard content remains intact.
css = r'''<style id="v107-stability-css">
/* V10.7 stability: never let enhancement layers cover the core question UI. */
[data-qb-route="practice"] .v105-cockpit,[data-qb-route="practice"] .v105-subjects,[data-qb-route="exam"] .v105-cockpit,[data-qb-route="exam"] .v105-subjects,[data-qb-route="review-test"] .v105-cockpit,[data-qb-route="review-test"] .v105-subjects{display:none!important}
</style>'''
if 'id="v107-stability-css"' not in s:
    s = s.replace('</head>', css + '\n</head>', 1)

HTML.write_text(s, encoding='utf-8')
print('V10.7 stabilization applied: fixed infinite option hint loop, confined subject cards to Home, exposed proven practice engine, and added route signalling.')
