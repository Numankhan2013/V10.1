  /* NK_QUESTION_HIGHLIGHTS_V1_START
   * Learner highlights in a question's explanation (key takeaway + explanation
   * section) in every bank. Presentation-only on top of nkStudySupport: the
   * markup gains a data-nk-hl-qid attribute, and a decorate pass wraps saved
   * ranges in <mark class="nk-hl"> after each render. Nothing else in the
   * study flow reads or writes these nodes.
   *
   * State: state.questionHighlights[qid] = {items:{[hid]:{id,zone,color,start,
   * end,quote,prefix,suffix,createdAt,updatedAt,deleted?}}}. Offsets count the
   * zone's text (see nkHlTextNodes); quote/prefix/suffix re-anchor a highlight
   * when the text shifts. Removing keeps a tombstone (deleted:true, newer
   * updatedAt) so cross_device_sync.js can merge item by item, newest edit wins.
   */
  const NK_HL_COLORS=['yellow','green','blue','pink','purple'];
  const NK_HL_COLOR_LABELS={yellow:'Yellow',green:'Green',blue:'Blue',pink:'Pink',purple:'Purple'};
  const NK_HL_CONTEXT=32,NK_HL_MAX_QUOTE=4000,NK_HL_MAX_ITEMS=200;
  const NK_HL_ZONES=[['takeaway','.nk-key-takeaway p'],['explanation','.nk-source-section']];
  // Text inside these never counts: chrome, controls and media, so offsets do not move when they change.
  const NK_HL_SKIP='button,svg,script,style,input,textarea,select,noscript,canvas,[contenteditable],[aria-hidden="true"],.nk-hl-skip';
  const NK_HL_STRUCTURE=/^(TABLE|THEAD|TBODY|TFOOT|TR|COLGROUP|UL|OL|DL)$/;

  function nkHlId(){return 'hl_'+Date.now().toString(36)+'_'+Math.random().toString(36).slice(2,8);}
  function nkHlSafeId(value){return /^[A-Za-z0-9_-]{1,64}$/.test(String(value||''));}
  // A stored item is trusted only after this: synced payloads are untrusted input.
  function nkHlCleanItem(raw){
    if(!raw||typeof raw!=='object'||!nkHlSafeId(raw.id))return null;
    const updatedAt=Math.max(0,Math.trunc(Number(raw.updatedAt)||0)),createdAt=Math.max(0,Math.trunc(Number(raw.createdAt)||updatedAt));
    if(raw.deleted)return {id:String(raw.id),deleted:true,updatedAt,createdAt};
    const start=Math.trunc(Number(raw.start)),end=Math.trunc(Number(raw.end)),quote=String(raw.quote||'').slice(0,NK_HL_MAX_QUOTE);
    if(!Number.isFinite(start)||!Number.isFinite(end)||start<0||end<=start||!quote)return null;
    return {id:String(raw.id),zone:raw.zone==='takeaway'?'takeaway':'explanation',color:NK_HL_COLORS.includes(raw.color)?raw.color:'yellow',start,end,quote,prefix:String(raw.prefix||'').slice(-NK_HL_CONTEXT),suffix:String(raw.suffix||'').slice(0,NK_HL_CONTEXT),createdAt,updatedAt};
  }
  // Item-level merge: per highlight the newer updatedAt wins (a tombstone is just a newer edit).
  function nkHlNewer(a,b){
    if(!b)return true;
    if(Number(a.updatedAt)!==Number(b.updatedAt))return Number(a.updatedAt)>Number(b.updatedAt);
    if(Boolean(a.deleted)!==Boolean(b.deleted))return Boolean(a.deleted); // tie: removal wins
    return JSON.stringify(a)>JSON.stringify(b);
  }
  function nkHlMergeItems(local,incoming){
    const out={};
    Object.values(local||{}).forEach(raw=>{const item=nkHlCleanItem(raw);if(item)out[item.id]=item;});
    (Array.isArray(incoming)?incoming:Object.values(incoming||{})).forEach(raw=>{const item=nkHlCleanItem(raw);if(item&&nkHlNewer(item,out[item.id]))out[item.id]=item;});
    return out;
  }
  function nkHlActive(items){return Object.values(items||{}).filter(item=>item&&!item.deleted).sort((a,b)=>a.createdAt-b.createdAt||String(a.id).localeCompare(String(b.id)));}

  // Resolve a stored range against the zone's current text: exact offsets first,
  // then the quote occurrence whose surrounding text best matches.
  function nkHlResolve(text,item){
    text=String(text||'');const quote=String(item?.quote||'');
    if(!quote)return null;
    const start=Number(item.start),end=Number(item.end);
    if(start>=0&&end<=text.length&&text.slice(start,end)===quote)return [start,end];
    const prefix=String(item.prefix||''),suffix=String(item.suffix||'');
    let best=null,from=0,seen=0;
    while(seen<500){
      const at=text.indexOf(quote,from);if(at<0)break;seen++;
      let score=0;
      for(let i=1;i<=prefix.length&&at-i>=0&&text[at-i]===prefix[prefix.length-i];i++)score++;
      for(let i=0;i<suffix.length&&at+quote.length+i<text.length&&text[at+quote.length+i]===suffix[i];i++)score++;
      const distance=Math.abs(at-start);
      if(!best||score>best.score||(score===best.score&&distance<best.distance))best={at,score,distance};
      from=at+1;
    }
    return best?[best.at,best.at+quote.length]:null;
  }
  function nkHlDescribe(text,start,end){
    text=String(text||'');
    // Trim surrounding whitespace so a sloppy touch selection does not tint gaps.
    while(start<end&&/\s/.test(text[start]))start++;
    while(end>start&&/\s/.test(text[end-1]))end--;
    if(end<=start)return null;
    return {start,end,quote:text.slice(start,end),prefix:text.slice(Math.max(0,start-NK_HL_CONTEXT),start),suffix:text.slice(end,end+NK_HL_CONTEXT)};
  }

  function nkHlEntry(qid){
    state.questionHighlights=state.questionHighlights&&typeof state.questionHighlights==='object'?state.questionHighlights:{};
    const key=String(qid);
    if(!state.questionHighlights[key]||typeof state.questionHighlights[key]!=='object')state.questionHighlights[key]={items:{}};
    const entry=state.questionHighlights[key];
    if(!entry.items||typeof entry.items!=='object')entry.items={};
    return entry;
  }
  function nkHlStamp(entry){
    // Strictly increasing per question, so an edit always beats the copy it replaces even on a slow clock.
    const latest=Math.max(0,...Object.values(entry.items).map(item=>Number(item.updatedAt)||0));
    return Math.max(Date.now(),latest+1);
  }
  function nkHlAdd(qid,zone,range,color){
    const entry=nkHlEntry(qid);
    if(nkHlActive(entry.items).length>=NK_HL_MAX_ITEMS)return null;
    const now=nkHlStamp(entry),item=nkHlCleanItem({id:nkHlId(),zone,color,...range,createdAt:now,updatedAt:now});
    if(!item)return null;
    entry.items[item.id]=item;return item;
  }
  function nkHlRecolor(qid,hid,color){
    const entry=nkHlEntry(qid),item=entry.items[hid];
    if(!item||item.deleted||!NK_HL_COLORS.includes(color)||item.color===color)return false;
    entry.items[hid]=nkHlCleanItem({...item,color,updatedAt:nkHlStamp(entry)});return true;
  }
  function nkHlRemove(qid,hid){
    const entry=nkHlEntry(qid),item=entry.items[hid];
    if(!item||item.deleted)return false;
    entry.items[hid]=nkHlCleanItem({id:item.id,deleted:true,createdAt:item.createdAt,updatedAt:nkHlStamp(entry)});return true;
  }
  function nkHlClear(qid){
    const entry=nkHlEntry(qid);let changed=0;
    nkHlActive(entry.items).forEach(item=>{if(nkHlRemove(qid,item.id))changed++;});
    return changed;
  }

  /* ---------------------------------------------------------------- DOM */
  function nkHlSkipped(node,zone){
    for(let el=node.parentElement;el&&el!==zone;el=el.parentElement){
      if(el.matches(NK_HL_SKIP))return true;
      // The section's own header ("Detailed explanation · Structured text") is chrome.
      if(el.tagName==='HEADER'&&el.parentElement===zone)return true;
    }
    return false;
  }
  function nkHlTextNodes(zone){
    const nodes=[],walker=document.createTreeWalker(zone,NodeFilter.SHOW_TEXT);
    let node,offset=0;
    while((node=walker.nextNode())){
      const value=node.nodeValue||'';
      if(!value)continue;
      if(!/\S/.test(value)&&NK_HL_STRUCTURE.test(node.parentElement?.tagName||''))continue;
      if(nkHlSkipped(node,zone))continue;
      nodes.push({node,start:offset,end:offset+value.length});offset+=value.length;
    }
    return {nodes,text:nodes.map(n=>n.node.nodeValue).join('')};
  }
  // Character offset in zone text of a DOM boundary point.
  function nkHlOffsetOf(zone,container,offset,nodes){
    if(container.nodeType===3){const hit=nodes.find(n=>n.node===container);if(hit)return hit.start+Math.min(offset,hit.end-hit.start);}
    const point=document.createRange();
    try{point.setStart(container,offset);}catch(_){return 0;}
    for(const n of nodes){if(point.comparePoint(n.node,0)>=0&&n.node!==container)return n.start;if(n.node===container)return n.start+offset;}
    return nodes.length?nodes[nodes.length-1].end:0;
  }
  function nkHlUnwrap(zone){
    const marks=zone.querySelectorAll('mark.nk-hl');
    if(!marks.length)return;
    marks.forEach(mark=>{const parent=mark.parentNode;if(!parent)return;while(mark.firstChild)parent.insertBefore(mark.firstChild,mark);parent.removeChild(mark);});
    zone.normalize();
  }
  function nkHlWrap(zone,item,range){
    const {nodes}=nkHlTextNodes(zone),[from,to]=range;let first=null,last=null;
    nodes.filter(n=>n.end>from&&n.start<to).forEach(n=>{
      let node=n.node;const a=Math.max(0,from-n.start),b=Math.min(n.end,to)-n.start;
      if(b<=a)return;
      if(b<node.nodeValue.length)node.splitText(b);
      if(a>0)node=node.splitText(a);
      if(!/\S/.test(node.nodeValue)&&!first)return; // no leading blank tint
      const mark=document.createElement('mark');
      mark.className='nk-hl';mark.dataset.nkHl=item.id;mark.dataset.nkHlColor=item.color;
      node.parentNode.insertBefore(mark,node);mark.appendChild(node);
      if(!first){first=mark;mark.classList.add('is-first');}
      last=mark;
    });
    // Only the ends are rounded, so a highlight running through bold or italic reads as one stroke.
    if(last)last.classList.add('is-last');
    return first;
  }
  function nkHlZones(root){
    return NK_HL_ZONES.map(([name,selector])=>{const el=root.querySelector(selector);if(el&&!el.dataset.nkHlZone)el.dataset.nkHlZone=name;return el?[name,el]:null;}).filter(Boolean);
  }
  // A plain-text source explanation is restructured by formatExplanations once;
  // decorate after that so the text being counted is the final text.
  function nkHlZoneSettled(zone){
    return ![...zone.querySelectorAll('.feedback-body')].some(el=>el.dataset.v102Formatted!=='1'&&!el.children.length&&(el.textContent||'').trim().length>=120);
  }
  function nkHlSignature(items){let h=2166136261;const s=JSON.stringify(items.map(i=>[i.id,i.color,i.start,i.end,i.quote]));for(let i=0;i<s.length;i++){h^=s.charCodeAt(i);h=Math.imul(h,16777619);}return (h>>>0).toString(36);}
  function nkHlDecorate(force=false){
    if(typeof document==='undefined')return;
    document.querySelectorAll('[data-nk-hl-qid]').forEach(root=>{
      const qid=root.dataset.nkHlQid,entry=state.questionHighlights?.[qid],all=entry?nkHlActive(entry.items):[];
      nkHlZones(root).forEach(([name,zone])=>{
        if(!nkHlZoneSettled(zone))return;
        const items=all.filter(item=>item.zone===name),sig=nkHlSignature(items),marks=zone.querySelectorAll('mark.nk-hl');
        const placed=new Set([...marks].map(m=>m.dataset.nkHl));
        if(!force&&zone.dataset.nkHlSig===sig&&placed.size===Number(zone.dataset.nkHlN||0))return;
        if(!items.length&&!marks.length){zone.dataset.nkHlSig=sig;zone.dataset.nkHlN='0';return;}
        nkHlUnwrap(zone);
        let shown=0;
        items.forEach(item=>{const text=nkHlTextNodes(zone).text,range=nkHlResolve(text,item);if(range&&nkHlWrap(zone,item,range))shown++;});
        zone.dataset.nkHlSig=sig;zone.dataset.nkHlN=String(shown);
      });
    });
  }

  /* ------------------------------------------------------------ toolbar */
  let nkHlBar=null,nkHlPending=null,nkHlEditing=null,nkHlPressed=0,nkHlSelTimer=0,nkHlPointerDown=false,nkHlClearArmed=0;
  const nkHlCoarse=()=>typeof matchMedia==='function'&&matchMedia('(pointer: coarse)').matches;
  function nkHlIcon(name){
    return name==='trash'
      ?'<svg width="16" height="16" viewBox="0 0 256 256" fill="currentColor" aria-hidden="true"><path d="M216,48H176V40a24,24,0,0,0-24-24H104A24,24,0,0,0,80,40v8H40a8,8,0,0,0,0,16h8V208a16,16,0,0,0,16,16H192a16,16,0,0,0,16-16V64h8a8,8,0,0,0,0-16ZM96,40a8,8,0,0,1,8-8h48a8,8,0,0,1,8,8v8H96Zm96,168H64V64H192ZM112,104v64a8,8,0,0,1-16,0V104a8,8,0,0,1,16,0Zm48,0v64a8,8,0,0,1-16,0V104a8,8,0,0,1,16,0Z"/></svg>'
      :'<svg width="12" height="12" viewBox="0 0 256 256" fill="currentColor" aria-hidden="true"><path d="M229.66,77.66l-128,128a8,8,0,0,1-11.32,0l-56-56a11.31,11.31,0,0,1,11.32-11.32L96,188.69,218.34,66.34a8,8,0,0,1,11.32,11.32Z"/></svg>';
  }
  function nkHlEnsureBar(){
    if(nkHlBar&&nkHlBar.isConnected)return nkHlBar;
    const bar=document.createElement('div');
    bar.className='nk-hl-bar';bar.setAttribute('role','toolbar');bar.setAttribute('aria-label','Highlight');bar.hidden=true;
    bar.innerHTML=NK_HL_COLORS.map(color=>`<button type="button" class="nk-hl-swatch" data-nk-hl-pick="${color}" aria-label="${NK_HL_COLOR_LABELS[color]} highlight" title="${NK_HL_COLOR_LABELS[color]}"><i data-nk-hl-color="${color}">${nkHlIcon('check')}</i></button>`).join('')+
      '<span class="nk-hl-sep" aria-hidden="true"></span><button type="button" class="nk-hl-act" data-nk-hl-act="remove" aria-label="Remove highlight" title="Remove highlight">'+nkHlIcon('trash')+'</button><button type="button" class="nk-hl-act nk-hl-clear" data-nk-hl-act="clear">Clear all</button>';
    // Pressing the bar must not end the selection it is about to colour.
    const press=event=>{nkHlPressed=Date.now();if(event.pointerType!=='touch'&&event.type!=='touchstart')event.preventDefault();};
    bar.addEventListener('pointerdown',press);bar.addEventListener('mousedown',event=>event.preventDefault());
    bar.addEventListener('click',nkHlBarClick);
    document.body.appendChild(bar);nkHlBar=bar;return bar;
  }
  function nkHlFeedback(){try{if(typeof nkPlayFeedback==='function')nkPlayFeedback('choice');}catch(_){}}
  function nkHlSave(){
    // saveState persists locally and queues the cloud upload; no render, so the reading position stays put.
    try{if(typeof saveState==='function')saveState();}catch(_){}
    nkHlDecorate();
  }
  function nkHlBarClick(event){
    const pick=event.target.closest('[data-nk-hl-pick]'),act=event.target.closest('[data-nk-hl-act]');
    if(pick){
      const color=pick.dataset.nkHlPick;
      if(nkHlEditing){nkHlRecolor(nkHlEditing.qid,nkHlEditing.hid,color);nkHlFeedback();nkHlSave();nkHlHide();return;}
      if(nkHlPending){
        const added=nkHlAdd(nkHlPending.qid,nkHlPending.zone,nkHlPending.range,color);
        try{window.getSelection()?.removeAllRanges();}catch(_){}
        nkHlPending=null;
        if(added){nkHlFeedback();nkHlSave();}
        else if(typeof showToast==='function')showToast('This question has reached its highlight limit.','bad');
        nkHlHide();
      }
      return;
    }
    if(act&&nkHlEditing){
      if(act.dataset.nkHlAct==='remove'){nkHlRemove(nkHlEditing.qid,nkHlEditing.hid);nkHlFeedback();nkHlSave();nkHlHide();return;}
      if(act.dataset.nkHlAct==='clear'){
        // Two taps: the first arms it, so one stray tap never wipes a question's highlights.
        if(Date.now()-nkHlClearArmed>3000){nkHlClearArmed=Date.now();act.textContent='Tap to confirm';act.classList.add('is-armed');return;}
        const n=nkHlClear(nkHlEditing.qid);nkHlFeedback();nkHlSave();nkHlHide();
        if(n&&typeof showToast==='function')showToast(n===1?'Highlight removed.':`${n} highlights removed.`);
      }
    }
  }
  function nkHlPlace(rect){
    const bar=nkHlEnsureBar();bar.hidden=false;
    const vw=document.documentElement.clientWidth||window.innerWidth,vh=window.innerHeight,w=bar.offsetWidth,h=bar.offsetHeight,gap=10;
    // Touch: the native Copy/Select-all menu sits above a selection, so go below it.
    const footer=document.querySelector('.nk-session-footer, .fixed-actions'),fr=footer?.getBoundingClientRect(),bottomLimit=fr&&fr.height>0&&fr.top>vh/2?Math.min(vh,fr.top):vh;
    const below=rect.bottom+gap,above=rect.top-gap-h;
    // Keep clear of the sticky session header (~56px) when going above.
    let top=nkHlCoarse()?(below+h<=bottomLimit-4?below:above):(above>=64?above:below);
    top=Math.max(8,Math.min(top,bottomLimit-h-4));
    const left=Math.max(8,Math.min(rect.left+rect.width/2-w/2,vw-w-8));
    bar.style.transform=`translate3d(${Math.round(left)}px,${Math.round(top)}px,0)`;
  }
  function nkHlShow(mode,rect,activeColor){
    const bar=nkHlEnsureBar();
    bar.dataset.mode=mode;nkHlClearArmed=0;
    const clear=bar.querySelector('.nk-hl-clear');clear.textContent='Clear all';clear.classList.remove('is-armed');
    clear.hidden=mode!=='edit'||!nkHlEditing||nkHlActive(nkHlEntry(nkHlEditing.qid).items).length<2;
    bar.querySelector('[data-nk-hl-act="remove"]').hidden=mode!=='edit';
    bar.querySelector('.nk-hl-sep').hidden=mode!=='edit';
    bar.querySelectorAll('[data-nk-hl-pick]').forEach(b=>{const on=b.dataset.nkHlPick===activeColor;b.classList.toggle('is-active',on);b.setAttribute('aria-pressed',on?'true':'false');});
    if(!rect){nkHlHide();return;}
    const fresh=bar.hidden;nkHlPlace(rect);
    if(fresh){bar.classList.remove('is-in');void bar.offsetWidth;bar.classList.add('is-in');}
  }
  function nkHlHide(){
    nkHlPending=null;nkHlEditing=null;
    if(nkHlBar){nkHlBar.hidden=true;nkHlBar.classList.remove('is-in');}
    document.querySelectorAll('mark.nk-hl.is-editing').forEach(m=>m.classList.remove('is-editing'));
  }
  function nkHlZoneOf(node){
    const el=node?.nodeType===1?node:node?.parentElement;
    const zone=el?.closest?.('[data-nk-hl-zone]'),root=zone?.closest('[data-nk-hl-qid]');
    return zone&&root?{zone,root}:null;
  }
  function nkHlFromSelection(){
    const sel=window.getSelection?.();
    if(!sel||!sel.rangeCount||sel.isCollapsed)return null;
    const range=sel.getRangeAt(0),hit=nkHlZoneOf(range.startContainer)||nkHlZoneOf(range.endContainer);
    if(!hit)return null;
    const {zone,root}=hit;
    const {nodes,text}=nkHlTextNodes(zone);
    const inStart=zone.contains(range.startContainer),inEnd=zone.contains(range.endContainer);
    const start=inStart?nkHlOffsetOf(zone,range.startContainer,range.startOffset,nodes):0;
    const end=inEnd?nkHlOffsetOf(zone,range.endContainer,range.endOffset,nodes):text.length;
    const described=nkHlDescribe(text,Math.min(start,end),Math.max(start,end));
    if(!described||described.quote.length>NK_HL_MAX_QUOTE)return null;
    return {qid:root.dataset.nkHlQid,zone:zone.dataset.nkHlZone,range:described,rect:range.getBoundingClientRect()};
  }
  function nkHlOnSelection(){
    clearTimeout(nkHlSelTimer);
    nkHlSelTimer=setTimeout(()=>{
      if(nkHlPointerDown)return; // mouse drag in progress: wait for the release
      const found=nkHlFromSelection();
      if(found){nkHlEditing=null;document.querySelectorAll('mark.nk-hl.is-editing').forEach(m=>m.classList.remove('is-editing'));nkHlPending=found;nkHlShow('create',found.rect,'');return;}
      if(nkHlBar&&!nkHlBar.hidden&&nkHlBar.dataset.mode==='create'&&Date.now()-nkHlPressed>600)nkHlHide();
    },nkHlCoarse()?220:60);
  }
  function nkHlEditRect(){
    const mark=nkHlEditing?.mark;if(!mark||!mark.isConnected)return null;
    const rects=[...document.querySelectorAll('mark.nk-hl.is-editing')].map(m=>m.getBoundingClientRect()),own=mark.getBoundingClientRect();
    return {top:Math.min(...rects.map(r=>r.top)),bottom:Math.max(...rects.map(r=>r.bottom)),left:own.left,width:own.width};
  }
  // The toolbar is fixed, so on scroll it follows its text, and closes once that text leaves the screen.
  function nkHlFollow(){
    if(!nkHlBar||nkHlBar.hidden)return;
    if(nkHlBar.dataset.mode==='edit'){
      const rect=nkHlEditRect();
      if(!rect||rect.bottom<0||rect.top>window.innerHeight){nkHlHide();return;}
      nkHlPlace(rect);return;
    }
    const sel=window.getSelection?.();
    if(sel&&sel.rangeCount&&!sel.isCollapsed){const rect=sel.getRangeAt(0).getBoundingClientRect();if(rect.bottom<0||rect.top>window.innerHeight)return;nkHlPlace(rect);}
  }
  function nkHlOnClick(event){
    if(nkHlBar&&nkHlBar.contains(event.target))return;
    const mark=event.target.closest?.('mark.nk-hl');
    const sel=window.getSelection?.();
    if(mark&&(!sel||sel.isCollapsed)&&!event.target.closest('a,button')){
      const root=mark.closest('[data-nk-hl-qid]');if(!root)return;
      const hid=mark.dataset.nkHl,qid=root.dataset.nkHlQid;
      document.querySelectorAll('mark.nk-hl.is-editing').forEach(m=>m.classList.remove('is-editing'));
      root.querySelectorAll('mark.nk-hl').forEach(m=>{if(m.dataset.nkHl===hid)m.classList.add('is-editing');});
      nkHlPending=null;nkHlEditing={qid,hid,mark};nkHlShow('edit',nkHlEditRect(),mark.dataset.nkHlColor);
      return;
    }
    if(nkHlBar&&!nkHlBar.hidden&&nkHlBar.dataset.mode==='edit')nkHlHide();
  }
  let nkHlFrame=0;
  function nkHlScheduleDecorate(){if(nkHlFrame)return;nkHlFrame=requestAnimationFrame(()=>{nkHlFrame=0;try{nkHlDecorate();}catch(error){console.warn('Highlights could not be drawn',error);}});}
  function nkHlInstall(){
    if(typeof document==='undefined'||typeof MutationObserver==='undefined'||!document.body)return;
    new MutationObserver(records=>{
      // Our own wrapping and the toolbar do not need another pass.
      if(records.every(r=>r.target===nkHlBar||nkHlBar?.contains(r.target)||[...r.addedNodes,...r.removedNodes].every(n=>n.nodeName==='MARK'||n.nodeType===3)))return;
      nkHlScheduleDecorate();
    }).observe(document.body,{childList:true,subtree:true});
    document.addEventListener('selectionchange',nkHlOnSelection);
    document.addEventListener('pointerdown',event=>{if(event.pointerType==='mouse'&&!(nkHlBar&&nkHlBar.contains(event.target))){nkHlPointerDown=true;if(nkHlBar&&!nkHlBar.hidden&&nkHlBar.dataset.mode==='create')nkHlHide();}},true);
    document.addEventListener('pointerup',event=>{if(event.pointerType==='mouse'&&nkHlPointerDown){nkHlPointerDown=false;nkHlOnSelection();}},true);
    document.addEventListener('click',nkHlOnClick);
    document.addEventListener('keydown',event=>{if(event.key==='Escape'&&nkHlBar&&!nkHlBar.hidden)nkHlHide();});
    let follow=0;
    document.addEventListener('scroll',()=>{if(!follow)follow=requestAnimationFrame(()=>{follow=0;nkHlFollow();});},{capture:true,passive:true});
    window.addEventListener('resize',()=>nkHlFollow());
    window.addEventListener('hashchange',nkHlHide);
    nkHlScheduleDecorate();
  }
  // Tag the explanation area with its question so the decorate pass and selections know where they are.
  const nkHlOriginalSupport=nkStudySupport;
  nkStudySupport=function(q){
    const html=nkHlOriginalSupport.apply(this,arguments);
    if(!q||q.id==null||typeof html!=='string')return html;
    return html.replace('<div class="nk-study-support','<div data-nk-hl-qid="'+esc(String(q.id))+'" class="nk-study-support');
  };
  nkHlInstall();
  /* NK_QUESTION_HIGHLIGHTS_V1_END */
