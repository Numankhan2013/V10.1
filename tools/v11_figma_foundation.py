from pathlib import Path

HTML = Path('app/src/main/assets/index.html')
s = HTML.read_text(encoding='utf-8')

css = r'''<style id="v11-figma-foundation">
/* QBank V11 Figma Foundation — visual layer only. No question/data logic. */
:root{
  --qbank-primary:#3FCFE8;
  --qbank-primary-strong:#177188;
  --qbank-primary-deep:#135262;
  --qbank-primary-soft:#E7FAFD;
  --qbank-bg:#F6F7FB;
  --qbank-surface:#FFFFFF;
  --qbank-ink:#171A2B;
  --qbank-muted:#6F7385;
  --qbank-line:#E4E6EF;
  --qbank-success:#159A68;
  --qbank-success-soft:#E2F7EF;
  --qbank-error:#D64B58;
  --qbank-error-soft:#FCE9EC;
  --qbank-amber:#D98B16;
  --qbank-radius:16px;
  --qbank-shadow:0 6px 20px rgba(23,32,51,.055);
}
html,body{background:var(--qbank-bg)!important;color:var(--qbank-ink)!important}
body{font-family:Inter,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif!important;font-size:15px;line-height:1.48}
.page{background:transparent!important;padding:20px 16px 34px!important}
.page-head{margin-bottom:18px!important}
.page-title{font-size:28px!important;line-height:1.12!important;letter-spacing:-.035em!important;color:var(--qbank-ink)!important}
.page-sub,.crumb,.label{color:var(--qbank-muted)!important}
.card{background:var(--qbank-surface)!important;border:1px solid var(--qbank-line)!important;border-radius:var(--qbank-radius)!important;box-shadow:var(--qbank-shadow)!important}
.card:hover{transform:none!important}
.primary-btn{background:var(--qbank-primary)!important;color:#0B3B45!important;border:0!important;border-radius:13px!important;min-height:46px!important;font-weight:800!important;box-shadow:none!important}
.ghost-btn{border-radius:13px!important;min-height:46px!important;font-weight:800!important}
.option-list{gap:9px!important}
.option{min-height:58px!important;border-radius:15px!important;border:1px solid var(--qbank-line)!important;background:#fff!important;box-shadow:none!important;padding:12px 14px!important}
.option.selected{border-color:var(--qbank-primary)!important;background:var(--qbank-primary-soft)!important;box-shadow:0 3px 12px rgba(63,207,232,.12)!important}
.option.correct{background:var(--qbank-success-soft)!important;border-color:var(--qbank-success)!important}
.option.incorrect{background:var(--qbank-error-soft)!important;border-color:var(--qbank-error)!important}
.option .radio,.qbank-session-page .option .radio{display:none!important}
.option-letter,.v105-option-letter{width:34px!important;height:34px!important;min-width:34px!important;border-radius:9px!important;display:grid!important;place-items:center!important;font-size:13px!important;font-weight:850!important;background:#F1F4F8!important;color:var(--qbank-ink)!important;margin-right:10px!important}
.option.selected .option-letter{background:var(--qbank-primary)!important;color:#0B3B45!important}
.option.correct .option-letter{background:var(--qbank-success)!important;color:#fff!important}
.option.incorrect .option-letter{background:var(--qbank-error)!important;color:#fff!important}
.qbank-session-page .question-card{border-radius:18px!important;box-shadow:var(--qbank-shadow)!important}
.qbank-session-page .question-text,.qbank-session-page .stem{font-size:16px!important;line-height:1.48!important}
.qbank-session-page .feedback{border-radius:15px!important}
.qbank-session-page .fixed-actions,.qbank-session-page .q-footer{gap:9px!important}
.qbank-session-page .fixed-actions .primary-btn,.qbank-session-page .q-footer .primary-btn{background:var(--qbank-primary)!important;color:#0B3B45!important}
/* Dashboard / home */
.qbank-route-dashboard .topbar{background:var(--qbank-primary-deep)!important;border-bottom:0!important;color:#fff!important}
.qbank-route-dashboard .brand{color:#fff!important}
.qbank-route-dashboard .page-title{font-size:28px!important}
.qbank-route-dashboard .qbank-continue{background:var(--qbank-primary)!important;color:#0B3B45!important;border:0!important}
.qbank-route-dashboard .qbank-next-card{background:var(--qbank-primary-strong)!important;color:#fff!important;border:0!important;box-shadow:none!important}
.qbank-route-dashboard .qbank-next-card .label,.qbank-route-dashboard .qbank-next-card small,.qbank-route-dashboard .qbank-next-card .muted{color:#DDF8FD!important}
.qbank-route-dashboard .qbank-next-card button:not(.primary-btn){background:#2B7F98!important;color:#fff!important;border:0!important}
.qbank-route-dashboard .qbank-subject-card{min-height:64px!important;padding:9px 12px!important}
.qbank-route-dashboard .qbank-subject-card:hover{transform:none!important}
.qbank-route-dashboard .qbank-streak-card{min-height:76px!important}
.qbank-route-dashboard .qbank-subject-card .label,.qbank-route-dashboard .qbank-streak-card .label{color:var(--qbank-muted)!important}
/* Analytics / custom module */
.qbank-route-insights .primary-btn,.qbank-route-analytics .primary-btn,
.qbank-route-custom-module .primary-btn{background:var(--qbank-primary)!important;color:#0B3B45!important}
.qbank-route-insights .card,.qbank-route-analytics .card,.qbank-route-custom-module .card{border-radius:16px!important}
@media(max-width:640px){
  .page{padding-left:14px!important;padding-right:14px!important}
  .page-title{font-size:27px!important}
  .option{min-height:56px!important}
}
</style>'''

if 'id="v11-figma-foundation"' not in s:
    s = s.replace('</head>', css + '\n</head>', 1)

js = r'''<script id="v11-figma-route-decoration">
(function(){
  'use strict';
  function markRoute(){
    var hash=(location.hash||'').replace(/^#/,'').replace(/[^a-zA-Z0-9_-]/g,'-')||'dashboard';
    document.body.className=document.body.className.replace(/\bqbank-route-[a-zA-Z0-9_-]+\b/g,'').trim();
    document.body.classList.add('qbank-route-'+hash);
  }
  function textOf(el){return (el&&el.textContent||'').replace(/\s+/g,' ').trim().toLowerCase();}
  function decorateDashboard(){
    if(!/^dashboard$/i.test((location.hash||'#dashboard').slice(1))) return;
    var cards=document.querySelectorAll('#app .card');
    cards.forEach(function(card){
      var t=textOf(card);
      if(t.indexOf('next best move')>=0) card.classList.add('qbank-next-card');
      if(t.indexOf('streak')>=0) card.classList.add('qbank-streak-card');
      if(/\b\d+\s+topics\b/.test(t)&&/\bq\b/.test(t)) card.classList.add('qbank-subject-card');
    });
    document.querySelectorAll('#app button,a').forEach(function(el){
      var t=textOf(el);
      if(t==='continue'||t==='continue studying') el.classList.add('qbank-continue');
    });
  }
  function apply(){markRoute();setTimeout(decorateDashboard,20);}
  window.addEventListener('hashchange',apply);
  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',apply); else apply();
})();
</script>'''
if 'id="v11-figma-route-decoration"' not in s:
    s = s.replace('</body>', js + '\n</body>', 1)

HTML.write_text(s, encoding='utf-8')
print('V11 Figma Foundation visual layer installed')
