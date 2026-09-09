/* Explicit question-ID bindings; source figures use the established touch viewer. */
(()=>{'use strict';
const mounted=new WeakSet();
function mount(){
  document.querySelectorAll('[data-marrow-question],[data-marrow-explanation]').forEach(node=>{
    if(mounted.has(node))return;
    mounted.add(node);
    const role=node.hasAttribute('data-marrow-question')?'question':'explanation';
    const id=node.getAttribute('data-marrow-'+role);
    const figures=(window.MARROW_VISUALS?.[id]||[]).filter(f=>f.role===role);
    if(!figures.length)return;
    const box=document.createElement('div');box.className='nk-marrow-figures';
    figures.forEach((figure,index)=>{
      const item=document.createElement('figure');
      const button=document.createElement('button');button.type='button';button.className='nk-marrow-figure-button';
      button.setAttribute('aria-label','Expand '+figure.alt);
      const img=document.createElement('img');img.src=(location.hostname==='qbank.local'?'/app/':'./')+figure.src;
      img.alt=figure.alt;img.width=figure.width;img.height=figure.height;
      img.loading=role==='question'?'eager':'lazy';img.decoding='async';
      img.addEventListener('error',()=>{button.disabled=true;caption.textContent='Image unavailable. Reconnect to download this figure.';});
      button.append(img);
      button.addEventListener('click',()=>window.NKSourceVisualViewer?.({type:'asset',source:figure.src},'Source figure '+(index+1)));
      const caption=document.createElement('figcaption');
      caption.textContent=(figures.length>1?'Figure '+(index+1)+' · ':'')+'Tap to expand'+(figure.status==='SOURCE_LIMITED'?' · Source image has limited detail':'');
      item.append(button,caption);box.append(item);
    });
    if(role==='question')node.after(box);else{
      const tail=node.querySelector('.nk-gold-wrong,.nk-marrow-provenance');
      if(tail)tail.before(box);else node.append(box);
    }
  });
}
const style=document.createElement('style');style.textContent='.nk-marrow-figures{display:grid;gap:16px;margin:14px 0 20px}.nk-marrow-figures figure{margin:0;min-width:0}.nk-marrow-figure-button{display:block;width:100%;padding:0;border:0;background:transparent;cursor:zoom-in}.nk-marrow-figure-button img{display:block;max-width:100%;width:auto;height:auto;max-height:72vh;object-fit:contain;margin:auto}.nk-marrow-figures figcaption{text-align:center;color:#6F7385;font-size:12px;margin-top:6px}.nk-marrow-figure-button:focus-visible{outline:2px solid #135262;outline-offset:4px}';
document.head.append(style);
new MutationObserver(mount).observe(document.documentElement,{childList:true,subtree:true});mount();
})();
