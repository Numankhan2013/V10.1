  /* NK_INTERACTION_POLISH_V1_START */
  // Press feedback starts at pointer-down, without waiting for click/persistence.
  // No pointer capture: vertical gestures continue to scroll naturally.
  let nkPress=null;
  function nkReleasePress(){nkPress?.node.classList.remove('nk-pressed');nkPress=null;}
  document.addEventListener('pointerdown',event=>{
    nkReleasePress();if(event.isPrimary===false||event.button>0)return;
    const node=event.target.closest?.('button,[role="button"],summary,a[href],[onclick]');
    if(!node||node.disabled||node.getAttribute('aria-disabled')==='true')return;
    nkPress={node,x:event.clientX,y:event.clientY};node.classList.add('nk-pressed');
  },{capture:true,passive:true});
  document.addEventListener('pointermove',event=>{
    if(nkPress&&Math.hypot(event.clientX-nkPress.x,event.clientY-nkPress.y)>9)nkReleasePress();
  },{passive:true});
  ['pointerup','pointercancel','dragstart'].forEach(name=>document.addEventListener(name,nkReleasePress,{capture:true,passive:true}));
  window.addEventListener('blur',nkReleasePress);
  const nkPolishMark=nkToggleExamReviewFlag;
  nkToggleExamReviewFlag=nkQuestionAction(nkPolishMark,()=>true,()=>{
    const button=document.querySelector('.nk-exam-review-toggle'),s=state.activeSession,id=s?.questionIds?.[s.index];
    if(!button||!id)return false;
    const marked=s.markedForReview?.[id]===true;
    button.classList.toggle('is-marked',marked);button.setAttribute('aria-pressed',String(marked));
    button.lastChild.textContent=marked?'Marked for review':'Mark for review';
    nkPlayFeedback('mark');return true;
  });
  const nkPolishRender=nkInteractionRender;
  let nkPolishIdentity='',nkPolishRoute='',nkPolishSubmitted=false;
  function nkPolishMotion(node,frames,duration=130){
    if(!node?.animate||window.matchMedia('(prefers-reduced-motion: reduce)').matches)return;
    node.animate(frames,{duration,easing:'cubic-bezier(.2,.7,.3,1)'});
  }
  render=function(){
    if(nkInteractionTransaction){nkInteractionTransaction.render=true;return;}
    const identity=['practice','exam','review-test'].includes(route.page)?nkQuestionIdentity():'';
    const same=identity&&identity===nkPolishIdentity&&route.page===nkPolishRoute;
    const x=window.scrollX,y=window.scrollY;
    const submitted=Boolean(state.activeSession?.submitted?.[state.activeSession?.questionIds?.[state.activeSession?.index]]);
    const keyboardAnswer=document.activeElement?.matches?.('.option');
    const open=same?[...document.querySelectorAll('.question-card details[open]')].map((node)=>node.id||node.className):[];
    nkPolishRender.apply(this,arguments);
    if(same){
      document.querySelectorAll('.question-card details').forEach(node=>{if(open.includes(node.id||node.className))node.open=true;});
      window.scrollTo(x,y);
      if(submitted&&!nkPolishSubmitted){
        nkPolishMotion(document.querySelector('.feedback'),[{transform:'translateY(2px)'},{transform:'translateY(0)'}],130);
        if(keyboardAnswer)document.querySelector('.nk-fsrs-pill,.nk-session-footer .primary-btn')?.focus({preventScroll:true});
      }
    }else if(identity){
      window.scrollTo(0,0);
      nkPolishMotion(document.querySelector('.question-card'),[{transform:'translateY(3px)'},{transform:'translateY(0)'}]);
    }else if(route.page!==nkPolishRoute){
      // Only the content moves; navigation and fixed controls stay mounted visually.
      nkPolishMotion(document.querySelector('.page'),[{transform:'translateY(3px)'},{transform:'translateY(0)'}],120);
    }
    nkPolishIdentity=identity;nkPolishRoute=route.page;nkPolishSubmitted=submitted;
  };
  // The transaction captured the old renderer before this late owner existed.
  // Route committed paints through the same final renderer, preserving rollback.
  nkInteractionRender=render;
  // A review sheet owns focus and scrolling until it closes. This changes no
  // session actions or dismissal contract, and restores the opener on close.
  let nkPolishOverlay=null,nkPolishOpener=null,nkPolishOverflow='';
  function nkPolishPanels(){
    const panels=[...document.querySelectorAll('.modal-backdrop,#nk-session-review,#qb-question-navigator')];
    const panel=panels.at(-1)||null;if(panel===nkPolishOverlay)return;
    if(!panel){
      if(nkPolishOverlay){document.body.style.overflow=nkPolishOverflow;if(nkPolishOpener?.isConnected)nkPolishOpener.focus({preventScroll:true});}
      nkPolishOverlay=null;nkPolishOpener=null;return;
    }
    if(!nkPolishOverlay){nkPolishOverflow=document.body.style.overflow;nkPolishOpener=document.activeElement;}
    nkPolishOverlay=panel;document.body.style.overflow='hidden';
    panel.querySelector('button:not(:disabled),input')?.focus({preventScroll:true});
    nkPolishMotion(panel.querySelector('.modal,.card')||panel.firstElementChild,[{transform:'translateY(5px) scale(.995)'},{transform:'translateY(0) scale(1)'}],140);
  }
  new MutationObserver(nkPolishPanels).observe(document.body,{childList:true,subtree:true});
  document.addEventListener('keydown',event=>{
    if(event.key!=='Tab'||!nkPolishOverlay)return;
    const nodes=[...nkPolishOverlay.querySelectorAll('button:not(:disabled),a[href],input:not(:disabled),select,textarea,[tabindex="0"]')].filter(node=>node.getClientRects().length);
    if(!nodes.length)return;
    const first=nodes[0],last=nodes.at(-1);
    if(event.shiftKey&&(document.activeElement===first||!nkPolishOverlay.contains(document.activeElement))){event.preventDefault();last.focus();}
    else if(!event.shiftKey&&(document.activeElement===last||!nkPolishOverlay.contains(document.activeElement))){event.preventDefault();first.focus();}
  });
  /* NK_INTERACTION_POLISH_V1_END */
