(function(){
  if(window.__NK_HOME_POLISH_V3__) return;
  window.__NK_HOME_POLISH_V3__=true;
  const css=`
  /* V3: structural visual reset — preserve existing DOM/workflows, change the hierarchy */
  .dashboard-v10{max-width:1000px!important;margin:0 auto!important;padding:0 0 24px!important;color:var(--ink)}
  .dashboard-v10 .dashboard-greeting{margin:0!important;padding:22px 4px 16px!important;display:flex;align-items:center;justify-content:space-between;gap:16px;border-bottom:1px solid #e5e7ef}
  .dashboard-v10 .dashboard-greeting h1{font-size:30px!important;line-height:1.08!important;letter-spacing:-1.3px!important;margin:3px 0 4px!important;font-weight:850!important}
  .dashboard-v10 .dashboard-greeting p{margin:0!important;color:#777985!important;font-size:14px!important}
  .dashboard-v10 .greet-kicker{font-size:11px!important;font-weight:800!important;letter-spacing:1.35px!important;color:#536aa5!important;text-transform:uppercase}
  .dashboard-v10 .greet-actions .primary-btn{min-height:44px!important;padding:0 18px!important;border-radius:12px!important;box-shadow:none!important;font-size:13px!important}

  /* The hero is now a command strip, not a floating card */
  .dashboard-v10 .focus-card{margin:0!important;border:0!important;border-radius:0!important;box-shadow:none!important;background:linear-gradient(110deg,#302d63 0%,#405fc6 72%,#4b67d0 100%)!important;padding:20px 20px 18px!important;min-height:0!important}
  .dashboard-v10 .focus-card:after{width:330px!important;height:330px!important;right:-155px!important;top:-165px!important;opacity:.35!important}
  .dashboard-v10 .focus-card .eyebrow{font-size:10px!important;letter-spacing:1.5px!important;opacity:.8}
  .dashboard-v10 .focus-card h2{font-size:21px!important;line-height:1.2!important;letter-spacing:-.35px!important;max-width:600px!important;margin:5px 0 5px!important}
  .dashboard-v10 .focus-card p{font-size:13px!important;line-height:1.4!important;max-width:610px!important;margin:0!important;opacity:.82}
  .dashboard-v10 .focus-actions{margin-top:14px!important;gap:8px!important}
  .dashboard-v10 .focus-btn{min-height:43px!important;border-radius:11px!important;padding:0 14px!important;font-size:13px!important;box-shadow:none!important}
  .dashboard-v10 .focus-btn.primary{box-shadow:none!important}

  /* Streak becomes an activity rail */
  .dashboard-v10 .streak-card-compact{margin:0!important;min-height:62px!important;padding:10px 16px!important;border:0!important;border-bottom:1px solid #e5e7ef!important;border-radius:0!important;box-shadow:none!important;background:#fff!important}
  .dashboard-v10 .streak-card-compact .streak-icon{width:40px!important;height:40px!important;border-radius:12px!important}
  .dashboard-v10 .streak-card-compact .streak-days{font-size:22px!important}

  /* Subject library is the main content surface */
  .dashboard-v10 .v102-subject-hub{margin:0!important;padding:20px 0 0!important;background:transparent!important;border:0!important;box-shadow:none!important}
  .dashboard-v10 .v102-section-head{padding:0 4px 9px!important}
  .dashboard-v10 .v102-section-head h2{font-size:24px!important;letter-spacing:-.9px!important;font-weight:850!important;margin:2px 0 0!important}
  .dashboard-v10 .v102-section-head span{font-size:12px!important;color:#767986!important}
  .dashboard-v10 .v102-eyebrow{font-size:10px!important;letter-spacing:1.5px!important;color:#536aa5!important;font-weight:850!important}
  .dashboard-v10 .v102-subject-grid{display:flex!important;flex-direction:column!important;gap:0!important;overflow:hidden!important;border:1px solid #e0e2ea!important;border-radius:14px!important;background:#fff!important;box-shadow:0 5px 18px rgba(32,34,58,.045)!important}
  .dashboard-v10 .v102-subject-card{min-height:74px!important;width:100%!important;border:0!important;border-bottom:1px solid #e9eaf0!important;border-radius:0!important;box-shadow:none!important;background:#fff!important;transform:none!important;padding-left:16px!important;padding-right:14px!important}
  .dashboard-v10 .v102-subject-card:last-child{border-bottom:0!important}
  .dashboard-v10 .v102-subject-card:hover{background:#f7f8fc!important}
  .dashboard-v10 .v102-subject-card.is-active{background:#f5f5fb!important;box-shadow:inset 3px 0 0 #3d65d8!important}
  .dashboard-v10 .v102-subject-card:active{background:#f1f2f8!important}

  /* Lower sections become quiet editorial lists */
  .dashboard-v10 .dashboard-section{margin-top:26px!important}
  .dashboard-v10 .dashboard-section>.section-title{margin-bottom:8px!important;padding:0 4px!important}
  .dashboard-v10 .status-grid,.dashboard-v10 .action-grid{border:1px solid #e1e3ea!important;border-radius:14px!important;background:#fff!important;box-shadow:none!important}
  .dashboard-v10 .status-card{min-height:72px!important;background:#fff!important}
  .dashboard-v10 .action-card{min-height:70px!important;background:#fff!important}
  .dashboard-v10 .grid.grid-2{gap:30px!important}
  .dashboard-v10 .grid.grid-2>.card,.dashboard-v10>.dashboard-section.card{border:0!important;border-top:1px solid #e1e3ea!important;border-radius:0!important;box-shadow:none!important;background:transparent!important;padding:15px 4px 0!important}
  .dashboard-v10 .chapter-mini{padding:11px 0!important}
  .dashboard-v10 .mini-card{padding:11px 0!important}
  .dashboard-v10>.dashboard-section.card{margin-top:30px!important}

  @media(max-width:560px){
    .dashboard-v10 .dashboard-greeting{padding:18px 0 14px!important;align-items:flex-end!important}
    .dashboard-v10 .dashboard-greeting h1{font-size:27px!important}
    .dashboard-v10 .dashboard-greeting p{font-size:13px!important;max-width:270px}
    .dashboard-v10 .greet-actions .primary-btn{min-height:42px!important;padding:0 13px!important;border-radius:11px!important}
    .dashboard-v10 .focus-card{padding:18px 16px 16px!important}
    .dashboard-v10 .focus-card h2{font-size:20px!important}
    .dashboard-v10 .v102-subject-hub{padding-top:18px!important}
    .dashboard-v10 .v102-section-head h2{font-size:23px!important}
  }
  `;
  const style=document.createElement('style');style.id='nk-home-polish-v3';style.textContent=css;document.head.appendChild(style);
  function enhance(root){if(!root||!root.classList||!root.classList.contains('dashboard-v10'))return;root.setAttribute('data-home-polished','v3');}
  const observer=new MutationObserver(function(){document.querySelectorAll('.dashboard-v10').forEach(enhance)});observer.observe(document.body,{childList:true,subtree:true});document.querySelectorAll('.dashboard-v10').forEach(enhance);
})();
