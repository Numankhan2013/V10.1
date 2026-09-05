from pathlib import Path

HTML = Path('app/src/main/assets/index.html')
s = HTML.read_text(encoding='utf-8')

css = r'''<style id="v11-figma-foundation-clean">
/* V11 visual foundation: layered on the verified V10.3.11 product baseline. */
:root{
  --v11-primary:#3FCFE8;
  --v11-primary-deep:#135262;
  --v11-primary-strong:#177188;
  --v11-primary-soft:#E7FAFD;
  --v11-bg:#F6F7FB;
  --v11-surface:#FFFFFF;
  --v11-ink:#171A2B;
  --v11-muted:#6F7385;
  --v11-line:#E4E6EF;
  --v11-success:#159A68;
  --v11-success-soft:#E2F7EF;
  --v11-error:#D64B58;
  --v11-error-soft:#FCE9EC;
}
html,body{background:var(--v11-bg)!important;color:var(--v11-ink)!important}
body{font-family:Inter,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif!important}
.topbar{background:var(--v11-primary-deep)!important}
.bottom-nav{background:rgba(255,255,255,.97)!important;border-top:1px solid var(--v11-line)!important}
.nav-item.active{color:var(--v11-primary)!important}
.page{padding-left:14px!important;padding-right:14px!important}
.card{border-color:var(--v11-line)!important;border-radius:16px!important;box-shadow:0 6px 20px rgba(23,32,51,.055)!important}
.primary-btn{background:var(--v11-primary)!important;color:#0B3B45!important;border:0!important;box-shadow:none!important;border-radius:13px!important;min-height:46px!important;font-weight:800!important}
.ghost-btn{border-radius:13px!important;min-height:46px!important}
.option-list{gap:9px!important}
.option{min-height:56px!important;padding:12px 14px!important;border-radius:15px!important;border:1px solid var(--v11-line)!important;box-shadow:none!important}
.option.selected{background:var(--v11-primary-soft)!important;border-color:var(--v11-primary)!important}
.option.correct{background:var(--v11-success-soft)!important;border-color:var(--v11-success)!important}
.option.wrong,.option.incorrect{background:var(--v11-error-soft)!important;border-color:var(--v11-error)!important}
/* V10.3.11 already established the letter-led option state; never reintroduce radio holes. */
.option .radio,.qbank-session-page .option .radio{display:none!important}
.option-letter,.v105-option-letter{width:34px!important;height:34px!important;min-width:34px!important;border-radius:9px!important;display:grid!important;place-items:center!important;background:#F1F4F8!important;color:var(--v11-ink)!important;font-weight:850!important;margin-right:10px!important}
.option.selected .option-letter{background:var(--v11-primary)!important;color:#0B3B45!important}
.option.correct .option-letter{background:var(--v11-success)!important;color:#fff!important}
.option.wrong .option-letter,.option.incorrect .option-letter{background:var(--v11-error)!important;color:#fff!important}
.qbank-session-page .question-card{border-radius:18px!important;box-shadow:0 6px 20px rgba(23,32,51,.055)!important}
.qbank-session-page .question-text,.qbank-session-page .stem{font-size:16px!important;line-height:1.48!important}
.qbank-session-page .feedback{border-radius:15px!important}
/* Keep the existing single HTML navigation bar. This V11 layer adds no native UI. */
</style>'''

if 'id="v11-figma-foundation-clean"' not in s:
    s = s.replace('</head>', css + '\n</head>', 1)

HTML.write_text(s, encoding='utf-8')
print('Clean V11 Figma foundation installed on the V10.3.11 baseline.')
