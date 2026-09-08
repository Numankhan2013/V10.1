(function(){
  if(window.__NK_HOME_POLISH_V2__) return;
  window.__NK_HOME_POLISH_V2__=true;
  const css = `
  .dashboard-v10{max-width:980px;margin:0 auto;padding:4px 0 18px;color:var(--ink)}
  .dashboard-v10 .dashboard-greeting{padding:0 2px 2px;align-items:flex-end;gap:18px}
  .dashboard-v10 .dashboard-greeting h1{margin:3px 0 2px;letter-spacing:-1px;font-weight:800}
  .dashboard-v10 .dashboard-greeting p{margin-top:4px;color:#686b79;line-height:1.35}
  .dashboard-v10 .greet-actions .primary-btn{min-height:54px;padding:0 24px;border-radius:17px;box-shadow:0 8px 20px rgba(61,101,216,.18);font-weight:800}
  .dashboard-v10 .focus-card{position:relative;overflow:hidden;margin-top:16px;border:0;border-radius:24px;box-shadow:0 16px 34px rgba(47,45,99,.16);background:linear-gradient(135deg,#302d63 0%,#405fc6 100%)}
  .dashboard-v10 .focus-card:after{width:260px;height:260px;right:-90px;top:-110px;opacity:.8}
  .dashboard-v10 .focus-card h2{max-width:650px;letter-spacing:-.35px}
  .dashboard-v10 .focus-actions{gap:10px}
  .dashboard-v10 .focus-btn{min-height:52px;border-radius:15px;padding:0 17px;transition:transform .14s ease,box-shadow .14s ease,background .14s ease}
  .dashboard-v10 .focus-btn.primary{box-shadow:0 5px 14px rgba(20,25,60,.14)}
  .dashboard-v10 .focus-btn:hover{transform:translateY(-1px)}
  .dashboard-v10 .streak-card-compact{margin-top:12px;min-height:76px;padding:14px 18px;border:1px solid #e9eaf0;border-radius:18px;box-shadow:none;background:rgba(255,255,255,.72)}
  .dashboard-v10 .streak-card-compact .streak-icon{width:48px;height:48px;border-radius:14px}
  .dashboard-v10 .streak-card-compact .streak-days{font-size:26px;line-height:1}
  .dashboard-v10 .v102-subject-hub{margin-top:18px;padding:0;background:transparent;border:0;box-shadow:none}
  .dashboard-v10 .v102-section-head{padding:0 2px 8px}
  .dashboard-v10 .v102-section-head h2{letter-spacing:-.7px;font-weight:800}
  .dashboard-v10 .v102-subject-grid{display:flex;flex-direction:column;gap:0;overflow:hidden;border-top:1px solid #e5e7ee;border-bottom:1px solid #e5e7ee;background:rgba(255,255,255,.58);border-radius:18px}
  .dashboard-v10 .v102-subject-card{min-height:78px;width:100%;border:0!important;border-radius:0!important;border-bottom:1px solid #e7e8ee!important;box-shadow:none!important;background:transparent!important;transform:none!important;transition:background .14s ease}
  .dashboard-v10 .v102-subject-card:last-child{border-bottom:0!important}
  .dashboard-v10 .v102-subject-card:hover{background:rgba(61,101,216,.035)!important}
  .dashboard-v10 .v102-subject-card.is-active{background:rgba(61,101,216,.055)!important}
  .dashboard-v10 .v102-subject-card:active{background:rgba(61,101,216,.08)!important}
  .dashboard-v10 .dashboard-section{margin-top:22px}
  .dashboard-v10 .dashboard-section>.section-title{margin-bottom:7px}
  .dashboard-v10 .status-grid{gap:0;overflow:hidden;border-top:1px solid #e5e7ee;border-bottom:1px solid #e5e7ee;border-radius:16px;background:rgba(255,255,255,.52)}
  .dashboard-v10 .status-card{min-height:78px;border:0!important;border-right:1px solid #e7e8ee!important;border-radius:0!important;box-shadow:none!important;background:transparent!important;transform:none!important}
  .dashboard-v10 .status-card:last-child{border-right:0!important}
  .dashboard-v10 .status-card:hover{transform:none;box-shadow:none;background:rgba(61,101,216,.025)!important}
  .dashboard-v10 .action-grid{gap:0;overflow:hidden;border-top:1px solid #e5e7ee;border-bottom:1px solid #e5e7ee;border-radius:16px;background:rgba(255,255,255,.52)}
  .dashboard-v10 .action-card{min-height:72px;border:0!important;border-right:1px solid #e7e8ee!important;border-bottom:1px solid #e7e8ee!important;border-radius:0!important;box-shadow:none!important;background:transparent!important;transform:none!important}
  .dashboard-v10 .action-card:nth-child(2n){border-right:0!important}
  .dashboard-v10 .action-card:nth-last-child(-n+2){border-bottom:0!important}
  .dashboard-v10 .action-card:hover{transform:none;box-shadow:none;background:rgba(61,101,216,.035)!important}
  .dashboard-v10 .action-card .action-icon{width:42px;height:42px;border-radius:13px;border:0;box-shadow:none}
  .dashboard-v10 .action-card .action-title{font-weight:800}
  .dashboard-v10 .grid.grid-2{gap:28px}
  .dashboard-v10 .grid.grid-2>.card,.dashboard-v10>.dashboard-section.card{border:0!important;border-top:1px solid #e3e5ec!important;border-radius:0!important;box-shadow:none!important;background:transparent!important;padding-left:2px;padding-right:2px}
  .dashboard-v10 .grid.grid-2>.card .section-title,.dashboard-v10>.dashboard-section.card .section-title{padding-top:3px}
  .dashboard-v10 .chapter-mini{padding:12px 4px;border-bottom:1px solid #ececf1}
  .dashboard-v10 .chapter-mini:last-child{border-bottom:0}
  .dashboard-v10 .chapter-mini .rank{border:0;background:#f1f2f7}
  .dashboard-v10 .mini-card{border:0!important;border-bottom:1px solid #ececf1!important;border-radius:0!important;box-shadow:none!important;background:transparent!important}
  .dashboard-v10 .mini-card:hover{transform:none;background:#f8f9fc!important}
  .dashboard-v10 .recent-row{border-radius:10px}
  .dashboard-v10 .eyebrow,.dashboard-v10 .v102-eyebrow{letter-spacing:1.2px}
  @media(max-width:760px){.dashboard-v10{padding:2px 0 14px}.dashboard-v10 .dashboard-greeting{align-items:flex-start;gap:12px}.dashboard-v10 .greet-actions .primary-btn{min-height:50px;padding:0 17px}.dashboard-v10 .focus-card{margin-top:14px;border-radius:22px}.dashboard-v10 .streak-card-compact{border-radius:16px}.dashboard-v10 .grid.grid-2{gap:22px}}
  @media(max-width:560px){.dashboard-v10 .dashboard-greeting{display:flex;flex-direction:column}.dashboard-v10 .greet-actions{width:100%}.dashboard-v10 .greet-actions .primary-btn{width:100%}.dashboard-v10 .focus-card{margin-top:12px}.dashboard-v10 .action-card{min-height:76px}}
  `;
  const style=document.createElement('style');style.id='nk-home-polish-v2';style.textContent=css;document.head.appendChild(style);
  function enhance(root){if(!root||!root.classList||!root.classList.contains('dashboard-v10'))return;root.setAttribute('data-home-polished','v2');const a=root.querySelector('.greet-actions');if(a)a.setAttribute('aria-label','Continue studying')}
  const observer=new MutationObserver(function(){document.querySelectorAll('.dashboard-v10').forEach(enhance)});observer.observe(document.body,{childList:true,subtree:true});document.querySelectorAll('.dashboard-v10').forEach(enhance);
})();
