from pathlib import Path
import re

HTML = Path('app/src/main/assets/index.html')
s = HTML.read_text(encoding='utf-8')

# Idempotent: remove any previous v2 layer before inserting the current one.
s = re.sub(r'<style id="qbank-question-ui-v2">.*?</style>\s*', '', s, flags=re.S)
s = re.sub(r'<script id="qbank-question-ui-v2-script">.*?</script>\s*', '', s, flags=re.S)

css = r'''<style id="qbank-question-ui-v2">
/* QBank Question UI v2
   Target: compact, calm mobile question presentation.
   Keep the question itself as the visual priority; do not alter question data,
   explanations, answer logic, persistence, or CBT behavior. */
.question-card {
  border-radius: 14px !important;
  box-shadow: 0 2px 10px rgba(24,30,58,.035) !important;
}
.question-card .q-head { margin-bottom: 0 !important; }
.question-card .q-actions { gap: 4px !important; }
.question-card .crumb {
  margin-bottom: 7px !important;
  font-size: 11px !important;
  line-height: 1.3 !important;
  font-weight: 700 !important;
}
.question-card .question-text {
  margin: 7px 0 11px !important;
  font-size: 16px !important;
  line-height: 1.43 !important;
  font-weight: 600 !important;
  letter-spacing: -0.12px !important;
}
.question-card .option-list { gap: 7px !important; }
.question-card .option {
  min-height: 46px !important;
  padding: 9px 11px !important;
  gap: 9px !important;
  border-radius: 11px !important;
  border-width: 1px !important;
  box-shadow: none !important;
}
.question-card .option-text {
  font-size: 15px !important;
  line-height: 1.34 !important;
  font-weight: 520 !important;
  letter-spacing: -0.08px !important;
}
.question-card .option-letter {
  width: 18px !important;
  font-size: 12px !important;
  padding-top: 2px !important;
}
.question-card .radio {
  width: 20px !important;
  height: 20px !important;
  border-width: 1.5px !important;
}
.question-card .selected .radio:after { width: 8px !important; height: 8px !important; }
.question-card .option.correct:after,
.question-card .option.wrong:after {
  width: 23px !important;
  height: 23px !important;
  right: 9px !important;
  top: 9px !important;
  font-size: 14px !important;
}
.question-card .feedback {
  margin-top: 11px !important;
  padding: 12px !important;
  border-radius: 12px !important;
}
.question-card .feedback-body {
  font-size: 13px !important;
  line-height: 1.55 !important;
}
.question-card .source-box {
  margin-top: 11px !important;
  padding: 10px 11px !important;
  border-radius: 11px !important;
}

/* The session page should not inherit dashboard/tool cards. If another layer
   injects these controls, remove only those controls while a question session
   is visible; dashboard and Topics/Test pages are untouched. */
@media (max-width: 700px) {
  .page { padding: 8px 10px calc(88px + var(--safe-bottom)) !important; }
  .page-head { margin-bottom: 8px !important; }
  .page-head .page-title { font-size: 22px !important; line-height: 1.08 !important; }
  .page-head .page-sub { font-size: 11px !important; line-height: 1.35 !important; }
  .page-head .mode-pill { font-size: 10px !important; padding: 5px 8px !important; }
  .question-shell { gap: 0 !important; }
  .question-card { padding: 11px !important; }
  .question-card .q-number { font-size: 11px !important; line-height: 1.25 !important; }
  .question-card .question-text { font-size: 16px !important; line-height: 1.42 !important; }
  .question-card .option-text { font-size: 15px !important; line-height: 1.34 !important; }
  .question-card .q-footer { margin-top: 11px !important; }
  .practice-actions { padding: 7px 9px !important; }
  .practice-actions .fixed-actions-inner { gap: 7px !important; }
  .practice-actions .ghost-btn,
  .practice-actions .primary-btn { min-height: 44px !important; padding: 0 9px !important; }
}

@media (min-width: 701px) {
  .question-card .question-text { font-size: 17px !important; line-height: 1.46 !important; }
  .question-card .option-text { font-size: 15px !important; line-height: 1.4 !important; }
}
</style>'''

script = r'''<script id="qbank-question-ui-v2-script">
(function(){
  function sessionVisible(){
    return !!document.querySelector('.question-card') &&
      !!document.querySelector('.question-shell, .practice-actions, .exam-top');
  }
  function cleanInjectedSessionCards(){
    if(!sessionVisible()) return;
    document.querySelectorAll('.page > *').forEach(function(el){
      if(el.matches('.question-shell,.page-head,.exam-top,.fixed-actions')) return;
      if(el.closest('.question-shell,.fixed-actions')) return;
      var text=(el.textContent||'').replace(/\s+/g,' ').trim().toLowerCase();
      var hasQuestion=el.querySelector('.question-card');
      if(hasQuestion) return;
      var explicitTool=el.matches('.focus-card,.action-grid,.dashboard-section,.action-card,.mode-choice,.v102-subject-hub');
      var accidentalLabel=/^(practice|timed cbt|cbt|your progress|your practice|performance)$/.test(text);
      if(explicitTool || accidentalLabel) el.remove();
    });
  }
  function run(){
    cleanInjectedSessionCards();
    var page=document.querySelector('.page');
    if(page && sessionVisible()) page.classList.add('qbank-session-ui-v2');
  }
  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',run);
  else setTimeout(run,30);
  setTimeout(run,250); setTimeout(run,700);
  new MutationObserver(run).observe(document.documentElement,{subtree:true,childList:true});
})();
</script>'''

if '</head>' not in s:
    raise SystemExit('Cannot apply question UI v2: </head> not found')
s = s.replace('</head>', css + '\n' + script + '\n</head>', 1)
HTML.write_text(s, encoding='utf-8')
print('Question UI v2 applied.')