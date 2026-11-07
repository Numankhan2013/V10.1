  /* NK_SESSION_CONTROLS_V1_START */
  // Keyboard and swipe controls for Practice and timed tests.
  // Keys: A–E or 1–5 answer, → / Enter next, ← previous, M mark for review (tests), ? shows the keys.
  // Swipe: left for next, right for previous, on the question itself.
  function nkControlsLive(){return (route?.page==='practice'||route?.page==='exam')&&['practice','exam'].includes(state.activeSession?.mode);}
  function nkControlsBlocked(target){
    if(document.querySelector('#nk-session-review,.qb-nav-backdrop,.nk-modal-backdrop,.nk-qs-backdrop,.nk-fs-viewer,[aria-modal="true"]'))return true;
    const el=target instanceof Element?target:null;
    return Boolean(el?.closest('input,textarea,select,[contenteditable="true"],[contenteditable=""],.nk-note-editor'));
  }
  function nkControlsOptions(){return [...document.querySelectorAll('.question-card .option-list > button.option')];}
  function nkControlsHelp(){
    const exam=state.activeSession?.mode==='exam';
    showToast(`Keys: A–E answer · → next · ← previous${exam?' · M mark for review':''}. Swipe the question left or right to move.`);
  }
  document.addEventListener('keydown',event=>{
    if(event.defaultPrevented||event.metaKey||event.ctrlKey||event.altKey||event.repeat&&!/^Arrow/.test(event.key))return;
    if(!nkControlsLive()||nkControlsBlocked(event.target))return;
    const key=event.key,lower=key.length===1?key.toLowerCase():key;
    const letter='abcde'.indexOf(lower),digit='12345'.indexOf(lower),choice=letter>=0?letter:digit;
    if(choice>=0){
      const options=nkControlsOptions();if(!options[choice])return;
      event.preventDefault();options[choice].click();options[choice].focus?.({preventScroll:true});return;
    }
    if(key==='ArrowRight'||key==='Enter'&&!(event.target instanceof Element&&event.target.closest('button,a,summary'))){event.preventDefault();window.QB.nextQ();return;}
    if(key==='ArrowLeft'){event.preventDefault();window.QB.prevQ();return;}
    if(lower==='m'&&state.activeSession?.mode==='exam'){const mark=document.querySelector('.nk-exam-review-toggle');if(mark){event.preventDefault();mark.click();}return;}
    if(key==='?'){event.preventDefault();nkControlsHelp();}
  });
  // A deliberate horizontal swipe on the question moves between questions. Scrollable tables,
  // zoomable figures and text selection keep their own gestures.
  let nkSwipe=null;
  function nkSwipeSkip(target){
    const el=target instanceof Element?target:null;if(!el)return true;
    if(el.closest('input,textarea,select,[contenteditable="true"],img,svg,canvas,.nk-fs-viewer,.nk-marrow-figure-button,.nk-note-editor'))return true;
    for(let node=el;node&&node!==document.body;node=node.parentElement){
      if(node.scrollWidth>node.clientWidth+4&&/(auto|scroll)/.test(getComputedStyle(node).overflowX))return true;
    }
    return false;
  }
  document.addEventListener('touchstart',event=>{
    nkSwipe=null;
    if(event.touches.length!==1||!nkControlsLive()||nkControlsBlocked(event.target))return;
    const shell=event.target instanceof Element&&event.target.closest('.question-shell');
    if(!shell||nkSwipeSkip(event.target))return;
    const t=event.touches[0];nkSwipe={x:t.clientX,y:t.clientY,at:Date.now(),shell};
  },{passive:true});
  document.addEventListener('touchmove',event=>{
    if(!nkSwipe||event.touches.length!==1)return;
    const t=event.touches[0],dx=t.clientX-nkSwipe.x,dy=t.clientY-nkSwipe.y;
    if(Math.abs(dy)>Math.abs(dx)&&Math.abs(dy)>12){nkSwipe.shell.style.removeProperty('--nk-swipe');nkSwipe=null;return;}
    if(Math.abs(dx)>12&&!window.getSelection?.()?.toString())nkSwipe.shell.style.setProperty('--nk-swipe',`${Math.max(-28,Math.min(28,dx/5))}px`);
  },{passive:true});
  function nkSwipeEnd(event){
    const s=nkSwipe;nkSwipe=null;if(!s)return;
    s.shell.style.removeProperty('--nk-swipe');
    const t=event.changedTouches?.[0];if(!t||event.type==='touchcancel')return;
    const dx=t.clientX-s.x,dy=t.clientY-s.y,ms=Date.now()-s.at;
    if(ms>700||Math.abs(dx)<72||Math.abs(dx)<Math.abs(dy)*1.8||window.getSelection?.()?.toString())return;
    if(typeof haptic==='function')haptic(6);
    if(dx<0)window.QB.nextQ();else window.QB.prevQ();
  }
  document.addEventListener('touchend',nkSwipeEnd,{passive:true});
  document.addEventListener('touchcancel',nkSwipeEnd,{passive:true});
  /* NK_SESSION_CONTROLS_V1_END */
