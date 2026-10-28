/* Explicit question-ID bindings; source figures use the established touch viewer. */
(()=>{'use strict';
const mounted=new WeakSet();
const HOLD_BYTES=8e6;
/* Figures are bundled files (a relative path) or, for PrepLadder's QBank, links to its image server. */
const url=src=>/^https:\/\//.test(src)?src:(location.hostname==='qbank.local'?'/app/':'./')+src;
const megabytes=bytes=>(bytes/1e6).toFixed(bytes<1e7?1:0)+' MB';
function mount(){
  document.querySelectorAll('[data-marrow-question],[data-marrow-explanation]').forEach(node=>{
    if(mounted.has(node))return;
    mounted.add(node);
    const role=node.hasAttribute('data-marrow-question')?'question':'explanation';
    const id=node.getAttribute('data-marrow-'+role);
    const figures=(window.MARROW_VISUALS?.[id]||[]).filter(f=>f.role===role);
    if(!figures.length)return;
    const box=document.createElement('div');box.className='nk-marrow-figures';
    /* An explanation that marks where its figures sat (a figure block) gets each one in place. */
    const slotOf=figure=>role==='explanation'&&figure.order!=null?node.querySelector('[data-marrow-figure="'+Number(figure.order)+'"]'):null;
    figures.forEach((figure,index)=>{
      const item=document.createElement('figure');
      const button=document.createElement('button');button.type='button';button.className='nk-marrow-figure-button';
      button.setAttribute('aria-label','Expand '+figure.alt);
      const img=document.createElement('img');
      img.alt=figure.alt;img.width=figure.width;img.height=figure.height;
      img.loading=role==='question'?'eager':'lazy';img.decoding='async';
      img.addEventListener('error',()=>{button.disabled=true;caption.textContent='Image unavailable. Reconnect to download this figure.';});
      const label=(figures.length>1?'Figure '+(index+1)+' · ':'')+'Tap to expand'+(figure.status==='SOURCE_LIMITED'?' · Source image has limited detail':'');
      const caption=document.createElement('figcaption');caption.textContent=label;
      /* Very large originals (long animations) wait for a tap instead of downloading on their own. */
      let held=(figure.bytes||0)>HOLD_BYTES;
      if(held){
        button.classList.add('is-held');button.style.aspectRatio=figure.width+' / '+figure.height;
        button.setAttribute('aria-label','Load '+figure.alt+' ('+megabytes(figure.bytes)+')');
        button.textContent='Tap to load · '+megabytes(figure.bytes);
        caption.textContent=(figures.length>1?'Figure '+(index+1)+' · ':'')+'Large figure';
      }else{img.src=url(figure.src);button.append(img);}
      button.addEventListener('click',()=>{
        if(held){held=false;button.classList.remove('is-held');button.style.aspectRatio='';button.textContent='';button.setAttribute('aria-label','Expand '+figure.alt);img.loading='eager';img.src=url(figure.src);button.append(img);caption.textContent=label;return;}
        window.NKSourceVisualViewer?.({type:'asset',source:figure.src},'Source figure '+(index+1));
      });
      item.append(button,caption);
      const slot=slotOf(figure);
      if(slot){const own=document.createElement('div');own.className='nk-marrow-figures';own.append(item);slot.replaceChildren(own);}
      else box.append(item);
    });
    if(!box.childElementCount)return;
    if(role==='question')node.after(box);else{
      const tail=node.querySelector('.nk-explain-refs,.nk-gold-wrong,.nk-marrow-provenance');
      if(tail)tail.before(box);else node.append(box);
    }
  });
}
const style=document.createElement('style');style.textContent='.nk-marrow-figures{display:grid;gap:16px;margin:14px 0 20px}.nk-marrow-figures figure{margin:0;min-width:0}.nk-marrow-figure-button{display:block;width:100%;padding:0;border:0;background:transparent;cursor:zoom-in}.nk-marrow-figure-button img{display:block;max-width:100%;width:auto;height:auto;max-height:72vh;object-fit:contain;margin:auto}.nk-marrow-figures figcaption{text-align:center;color:#6F7385;font-size:12px;margin-top:6px}.nk-marrow-figure-button.is-held{max-height:60vh;border:1px dashed var(--nkg-border-strong,#c9c9c9);border-radius:12px;color:var(--nkg-fg-2,#555);font-weight:500;font-size:14px;line-height:1.3;cursor:pointer}.nk-marrow-figure-button:focus-visible{outline:2px solid #135262;outline-offset:4px}';
document.head.append(style);
new MutationObserver(mount).observe(document.documentElement,{childList:true,subtree:true});mount();
})();
