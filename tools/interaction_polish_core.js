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
  // Dense activity data stays a compact chart. One tab stop, spatial arrow
  // navigation and explicit activation replace hundreds of tab stops.
  document.addEventListener('keydown',event=>{
    const button=event.target.closest?.('.nk-li-year-grid button');
    if(!button)return;
    const keys={ArrowLeft:-7,ArrowRight:7,ArrowUp:-1,ArrowDown:1};
    if(!(event.key in keys)&&!['Home','End'].includes(event.key))return;
    const buttons=[...button.closest('.nk-li-year-grid').querySelectorAll('button:not(:disabled)')],index=buttons.indexOf(button);
    const next=event.key==='Home'?0:event.key==='End'?buttons.length-1:Math.max(0,Math.min(buttons.length-1,index+keys[event.key]));
    event.preventDefault();buttons.forEach((node,i)=>node.tabIndex=i===next?0:-1);
    buttons[next]?.focus({preventScroll:true});buttons[next]?.scrollIntoView({block:'nearest',inline:'nearest',behavior:'instant'});
  });
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
  // Only the answer region and newly revealed support change after the existing
  // durable submit. Keep the question, figures and header mounted while reading.
  function nkPatchPracticeOutcome(){
    const s=state.activeSession,q=nkCurrentQuestion(),card=document.querySelector('.is-practice .question-card');
    if(route.page!=='practice'||!q||!s?.submitted?.[q.id]||!card||card.querySelector('.nk-study-support'))return false;
    const options=card.querySelector('.option-list'),footer=document.querySelector('.nk-session-footer');
    if(!options||!footer)return false;
    const selected=s.answers[q.id]||null,template=document.createElement('template');
    template.innerHTML=`<div class="option-list">${nkSessionOptions(q,selected,'practice',true)}</div>${nkStudySupport(q,s.questionTimes?.[q.id]||0,false)}${practiceActionBar(s,q,selected,true)}`;
    const nextOptions=template.content.querySelector('.option-list'),nextFooter=template.content.querySelector('.nk-session-footer');
    if(!nextOptions||!nextFooter||nextOptions.children.length!==options.children.length)return false;
    const keyboardAnswer=document.activeElement?.matches('.option'),x=window.scrollX,y=window.scrollY;
    options.replaceChildren(...nextOptions.childNodes);
    nextFooter.remove();while(nextOptions.nextSibling)card.appendChild(nextOptions.nextSibling);
    footer.replaceWith(nextFooter);nkMountQuestionNote();nkPolishOutcome();
    window.scrollTo(x,y);
    if(keyboardAnswer)document.querySelector('.nk-fsrs-pill.is-default,.nk-session-footer .primary-btn')?.focus({preventScroll:true});
    nkPolishIdentity=nkQuestionIdentity();nkPolishRoute=route.page;nkPolishSubmitted=true;
    return true;
  }
  function nkPolishOutcome(){
    if(!['practice','review-test'].includes(route.page))return;
    const s=state.activeSession,q=nkCurrentQuestion(),support=document.querySelector('.nk-study-support');
    if(!q||!support||support.querySelector('.nk-answer-outcome'))return;
    const selected=Number(s?.answers?.[q.id]),correct=selected===Number(q.correctOption);
    const letter=(q.options||[]).find(o=>String(o.letter).toUpperCase().charCodeAt(0)-64===Number(q.correctOption))?.letter;
    if(!letter)return;
    const status=document.createElement('p');status.className='nk-answer-outcome '+(correct?'is-correct':selected?'is-wrong':'is-unattempted');
    status.setAttribute('role','status');status.textContent=`${correct?'Correct · Answer':selected?'Incorrect · Correct answer':'Unattempted · Correct answer'} ${letter}`;
    support.prepend(status);
  }
  // Local mode switches keep the keyboard on its control and retain the reading
  // position. No timer or animation gates the replacement.
  function nkPolishReplaceSurface(node,markup){
    if(!node)return;
    const controls=[...node.querySelectorAll('button,select,summary')],index=controls.indexOf(document.activeElement),x=window.scrollX,y=window.scrollY;
    const template=document.createElement('template');template.innerHTML=markup;
    const next=template.content.firstElementChild;if(!next)return;
    node.replaceWith(next);
    if(index>=0)next.querySelectorAll('button,select,summary')[index]?.focus({preventScroll:true});
    window.scrollTo(x,y);return next;
  }
  render=function(){
    if(nkInteractionTransaction){nkInteractionTransaction.render=true;return;}
    const identity=['practice','exam','review-test'].includes(route.page)?nkQuestionIdentity():'';
    const same=identity&&identity===nkPolishIdentity&&route.page===nkPolishRoute;
    const x=window.scrollX,y=window.scrollY;
    const submitted=Boolean(state.activeSession?.submitted?.[state.activeSession?.questionIds?.[state.activeSession?.index]]);
    const keyboardAnswer=document.activeElement?.matches?.('.option');
    const footerFocus=[...document.querySelectorAll('.nk-session-footer .fixed-actions-inner button')].indexOf(document.activeElement);
    const open=same?[...document.querySelectorAll('.question-card details[open]')].map((node)=>node.id||node.className):[];
    const builder=document.querySelector('.nk-module-builder'),builderTitle=builder?.querySelector('h1')?.textContent;
    const builderAction=builder?.contains(document.activeElement)?document.activeElement?.getAttribute('onclick'):null;
    nkPolishRender.apply(this,arguments);
    const nextBuilder=document.querySelector('.nk-module-builder');
    if(builderAction&&builderTitle===nextBuilder?.querySelector('h1')?.textContent){
      [...nextBuilder.querySelectorAll('button')].find(n=>n.getAttribute('onclick')===builderAction)?.focus({preventScroll:true});
      window.scrollTo(x,y);
    }
    nkPolishOutcome();
    if(same){
      document.querySelectorAll('.question-card details').forEach(node=>{if(open.includes(node.id||node.className))node.open=true;});
      window.scrollTo(x,y);
      if(submitted&&!nkPolishSubmitted){
        if(keyboardAnswer)document.querySelector('.nk-fsrs-pill,.nk-session-footer .primary-btn')?.focus({preventScroll:true});
      }
    }else if(identity){
      window.scrollTo(0,0);
      if(footerFocus>=0&&route.page===nkPolishRoute){
        const buttons=document.querySelectorAll('.nk-session-footer .fixed-actions-inner button');
        (buttons[footerFocus]?.disabled?buttons[1]:buttons[footerFocus])?.focus({preventScroll:true});
      }
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
