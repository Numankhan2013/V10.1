from pathlib import Path
import re

HTML = Path('app/src/main/assets/index.html')
s = HTML.read_text(encoding='utf-8')

# V10.8 intentionally keeps the old engine. Make that contract stricter: remove
# duplicate/legacy experience runtimes rather than allowing observers to mutate
# question, exam, review, or topic DOM.
def replace_all_scripts(text, script_id, body):
    pat = r'<script id="' + re.escape(script_id) + r'">.*?</script>'
    return re.sub(pat, '<script id="' + script_id + '">' + body + '</script>', text, flags=re.S)

# V10.4's backup runtime contains the real backup implementation. Its visual
# enhance() is already neutralised by V10.8; leave the backup engine intact.
# V10.4.1 is purely dashboard decoration and is disabled completely.
s = replace_all_scripts(s, 'v104-1-runtime', "(function(){'use strict';})();")

# Replace every V10.5 runtime, not just the first one. This is important because
# repeated MutationObservers were the source of the runaway question hint bug.
s = replace_all_scripts(s, 'v105-runtime', "(function(){'use strict';})();")

css = r'''<style id="v109-fidelity-polish">
/* Fidelity-first product polish: visual only, no question-engine DOM surgery. */
:root{--v109-bg:#f6f8fc;--v109-surface:#fff;--v109-text:#172033;--v109-muted:#6c778a;--v109-line:#e6eaf1;--v109-primary:#4054d8;--v109-radius:18px}
html,body{background:var(--v109-bg)!important;color:var(--v109-text)!important}
body{font-size:15px;line-height:1.5;padding-bottom:92px!important}
.topbar{min-height:62px!important;padding:0 16px!important;background:rgba(246,248,252,.94)!important;border-bottom:1px solid var(--v109-line)!important;box-shadow:0 1px 0 rgba(20,30,50,.02)!important}
.brand{font-size:18px!important;font-weight:850!important;letter-spacing:-.025em!important}
.page{max-width:1000px!important;padding:22px 16px 38px!important}
.page-head{margin-bottom:18px!important}
.page-title{font-size:30px!important;line-height:1.12!important;letter-spacing:-.04em!important}
.page-sub,.crumb,.label{color:var(--v109-muted)!important}
.card{border:1px solid var(--v109-line)!important;border-radius:var(--v109-radius)!important;box-shadow:0 7px 22px rgba(28,40,70,.055)!important;background:rgba(255,255,255,.97)!important}
.card:hover{transform:none!important;box-shadow:0 9px 26px rgba(28,40,70,.075)!important}
.primary-btn,.ghost-btn{min-height:46px!important;border-radius:13px!important;padding:10px 16px!important;font-weight:800!important}
.primary-btn{box-shadow:0 5px 15px rgba(64,84,216,.18)!important}
.option-list{gap:10px!important}
.option{min-height:60px!important;border-radius:15px!important;border:1px solid var(--v109-line)!important;background:#fff!important;box-shadow:none!important;transform:none!important;padding:14px 16px!important}
.option:hover{transform:none!important;box-shadow:0 3px 12px rgba(28,40,70,.05)!important}
.option.selected{box-shadow:0 4px 15px rgba(64,84,216,.09)!important}
.feedback{border-radius:15px!important}
.fixed-actions,.q-footer{padding-bottom:6px!important;gap:9px!important}
/* Make subject selectors feel like real app controls without changing their markup. */
.v102-subject-mark{width:46px!important;height:46px!important;border-radius:14px!important;display:grid!important;place-items:center!important;font-weight:900!important;font-size:13px!important;letter-spacing:.02em!important;flex:none!important;background:linear-gradient(135deg,#eef0ff,#f7f7ff)!important;color:#4050bd!important;border:1px solid #dfe3fb!important}
/* Remove decorative legacy blocks if one survives a route transition. */
.v104-command,.v104-grid,.v104-backup,.v105-cockpit,.v105-subjects{display:none!important}
/* Practice hub remains a deliberate entry point; keep it compact and readable. */
.v108-practice-grid{gap:12px!important;margin-top:16px!important}
.v108-practice-card{border-radius:17px!important;min-height:96px!important;box-shadow:0 6px 18px rgba(28,40,70,.055)!important}
.v108-icon{border-radius:12px!important}
@media(max-width:640px){.page{padding-left:14px!important;padding-right:14px!important}.page-title{font-size:28px!important}.v108-practice-card{min-height:84px!important}}
</style>'''
if 'id="v109-fidelity-polish"' not in s:
    s = s.replace('</head>', css + '\n</head>', 1)

# A small route-aware guard only removes legacy decorative nodes. It never adds
# content and never observes question options, explanations, CBT answers, or
# test controls. The working HTML engine remains the sole renderer.
cleanup = r'''<script id="v109-fidelity-runtime">
(function(){'use strict';
function clean(){
  ['.v104-command','.v104-grid','.v104-backup','.v105-cockpit','.v105-subjects'].forEach(function(sel){
    document.querySelectorAll(sel).forEach(function(el){el.remove();});
  });
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',clean);else clean();
})();
</script>'''
if 'id="v109-fidelity-runtime"' not in s:
    s = s.replace('</body>', cleanup + '\n</body>', 1)

# Ensure the native bottom bar cannot cover the HTML engine's fixed controls.
java = Path('app/src/main/java/com/qbank/biochemistry/MainActivity.java')
if java.exists():
    j = java.read_text(encoding='utf-8')
    j = j.replace('webLp.bottomMargin = dp(92);', 'webLp.bottomMargin = dp(92);')
    java.write_text(j, encoding='utf-8')

HTML.write_text(s, encoding='utf-8')
print('V10.9 fidelity-first polish installed')
