(function(){
  if(window.__NK_HOME_POLISH_V1__) return;
  window.__NK_HOME_POLISH_V1__=true;

  const css = `
  /* NK QBank Home Polish v1 — presentation only. Question UI remains untouched. */
  .dashboard-v10{max-width:960px;margin:0 auto;padding-bottom:8px}
  .dashboard-v10 .dashboard-greeting{padding:2px 2px 0}
  .dashboard-v10 .dashboard-greeting h1{letter-spacing:-.7px}
  .dashboard-v10 .greet-actions .primary-btn{box-shadow:0 6px 16px rgba(61,101,216,.14)}
  .dashboard-v10 .focus-card{border-radius:20px;box-shadow:0 10px 28px rgba(47,45,99,.13);background:linear-gradient(135deg,#302d63 0%,#405fc6 100%)}
  .dashboard-v10 .focus-card:after{width:190px;height:190px;right:-60px;top:-70px}
  .dashboard-v10 .focus-btn{transition:transform .14s ease,background .14s ease,box-shadow .14s ease}
  .dashboard-v10 .focus-btn:hover{transform:translateY(-1px);box-shadow:0 5px 14px rgba(20,25,60,.13)}
  .dashboard-v10 .focus-btn.primary{box-shadow:0 4px 12px rgba(15,20,50,.12)}
  .dashboard-v10 .streak-card-compact{border-color:#eee5cf;box-shadow:0 4px 16px rgba(50,43,20,.045)}
  .dashboard-v10 .v102-subject-hub{padding:2px 0 0}
  .dashboard-v10 .v102-subject-grid{gap:10px}
  .dashboard-v10 .v102-subject-card{min-height:82px;border-radius:17px;transition:transform .14s ease,box-shadow .14s ease,border-color .14s ease}
  .dashboard-v10 .v102-subject-card:hover{transform:translateY(-1px);box-shadow:0 6px 16px rgba(31,36,61,.08)}
  .dashboard-v10 .v102-subject-card.is-active{box-shadow:0 0 0 2px rgba(61,101,216,.11),0 6px 16px rgba(31,36,61,.07)}
  .dashboard-v10 .dashboard-section>.section-title{margin-bottom:9px}
  .dashboard-v10 .status-grid{gap:9px}
  .dashboard-v10 .status-card{min-height:91px;border-radius:16px;box-shadow:0 3px 12px rgba(25,27,48,.035);transition:box-shadow .14s ease,transform .14s ease}
  .dashboard-v10 .status-card:hover{transform:translateY(-1px);box-shadow:0 6px 16px rgba(25,27,48,.07)}
  .dashboard-v10 .action-grid{gap:10px}
  .dashboard-v10 .action-card{min-height:106px;border-radius:17px;box-shadow:0 3px 12px rgba(25,27,48,.04);transition:transform .14s ease,box-shadow .14s ease,border-color .14s ease}
  .dashboard-v10 .action-card:hover{transform:translateY(-1px);box-shadow:0 7px 18px rgba(25,27,48,.075)}
  .dashboard-v10 .action-card:active,.dashboard-v10 .status-card:active,.dashboard-v10 .v102-subject-card:active{transform:translateY(0)}
  .dashboard-v10 .action-card .action-icon{border:1px solid rgba(50,55,90,.055)}
  .dashboard-v10 .grid.grid-2>.card{border-radius:18px;box-shadow:0 3px 14px rgba(25,27,48,.04)}
  .dashboard-v10 .chapter-mini{padding:12px 0}
  .dashboard-v10 .chapter-mini .rank{border:1px solid #e1e4ef}
  .dashboard-v10 .mini-card{border-radius:13px;box-shadow:none;transition:background .14s ease,border-color .14s ease,transform .14s ease}
  .dashboard-v10 .mini-card:hover{transform:translateY(-1px);background:#fbfcff}
  .dashboard-v10 .recent-row{border-radius:12px;transition:background .14s ease}
  .dashboard-v10 .recent-row:hover{background:#f7f8fc!important}
  .dashboard-v10 .recent-row:focus-visible,.dashboard-v10 .action-card:focus-visible,.dashboard-v10 .status-card:focus-visible,.dashboard-v10 .v102-subject-card:focus-visible{outline:3px solid rgba(61,101,216,.16);outline-offset:2px}
  @media(max-width:760px){
    .dashboard-v10{padding-bottom:2px}
    .dashboard-v10 .focus-card{border-radius:18px}
    .dashboard-v10 .v102-subject-card{min-height:78px}
  }
  @media(max-width:520px){
    .dashboard-v10 .dashboard-greeting{padding-top:0}
    .dashboard-v10 .status-card{min-height:84px}
    .dashboard-v10 .action-card{min-height:104px}
  }
  `;
  const style=document.createElement('style');
  style.id='nk-home-polish-v1'; style.textContent=css; document.head.appendChild(style);

  function enhance(root){
    if(!root || !root.classList || !root.classList.contains('dashboard-v10')) return;
    root.setAttribute('data-home-polished','v1');
    const actions=root.querySelector('.greet-actions');
    if(actions) actions.setAttribute('aria-label','Continue studying');
  }

  const observer=new MutationObserver(function(){
    document.querySelectorAll('.dashboard-v10').forEach(enhance);
  });
  observer.observe(document.body,{childList:true,subtree:true});
  document.querySelectorAll('.dashboard-v10').forEach(enhance);
})();
