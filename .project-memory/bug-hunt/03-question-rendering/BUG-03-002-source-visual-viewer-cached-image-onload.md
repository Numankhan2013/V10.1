# BUG-03-002 — Source visual viewers attach `load` handlers after setting `src`, so cached images never fit/zoom

- **Area:** 03 question rendering
- **Severity:** medium
- **Confidence:** high
- **Status:** fix applied — commit 8b961133
- **Files:** `app/src/main/assets/source_visual_renderer.js:10`, `app/src/main/assets/source_visual_renderer.js:19`, `app/src/main/assets/index.html:1389`
- **Introduced by:** unknown

## What happens

Both visual viewers set the image `src` before attaching the `load` handler that sizes/zooms the image. When the browser serves the image from cache, the `load` event can fire before the handler is attached, so `fit()` / `resetPhysZoom()` never runs and the image stays at its intrinsic size (or the zoom transform is never applied).

## Evidence

`source_visual_renderer.js` viewer:

```js
var img=bd.querySelector('.nk-sv-img'),st=bd.querySelector('.nk-sv-stage');img.src=url;
...
img.onload=fit;   // attached after src is set
```

Physiology source zoom in `index.html`:

```js
b.innerHTML=`...<img class="phys-zoom-image" src="${img.src}" ...>...`;
...
const i=b.querySelector('.phys-zoom-image'); ... i.addEventListener('load',()=>resetPhysZoom());
```

In both cases the `src` is committed (and may load from cache synchronously) before the listener exists.

## Learner impact

A cached source figure opens in the viewer without being fitted to the stage, or the physiology zoom image never gets its initial scale/centering, making the viewer unusable until a manual reset. Recoverable (Reset button), but breaks the primary open-figure flow on repeat views.

## Root cause

Listener registration happens after resource assignment. Cached resources can complete before the listener exists, so the initial layout callback is lost.

## Proposed fix

Attach the handler before assigning `src`, and call the layout function immediately if the image is already complete.

```diff
--- a/app/src/main/assets/source_visual_renderer.js
+++ b/app/src/main/assets/source_visual_renderer.js
@@ -7,7 +7,7 @@
 function route(v){if(!v)return null;if(v.type==='asset'&&v.source)return (location.hostname==='qbank.local'?'/app/':'./')+String(v.source).replace(/^\/+/, '');if(v.type!=='source-pdf'||!v.source||!v.page)return null;var s=String(v.source).toLowerCase(),p=s.indexOf('anatomy')>=0?'anatomy':s.indexOf('physiology')>=0?'physiology':'biochemistry',q=['page='+encodeURIComponent(v.page),'scale='+encodeURIComponent(v.scale||8)];if(v.crop)['top','bottom','left','right'].forEach(function(k){if(v.crop[k]!=null)q.push(k+'='+encodeURIComponent(v.crop[k]));});return 'https://qbank.local/'+p+'/pdf?'+q.join('&');}
 function activePracticeVisual(card){if(!card||!(card.closest('.nk-v113-question')||card.closest('.nk-v114-session')))return null;try{var state=window.QB&&window.QB.getState&&window.QB.getState(),session=state&&state.activeSession,id=session&&Array.isArray(session.questionIds)?session.questionIds[session.index]:null;return id&&BY_QID[id]?BY_QID[id]:null;}catch(_){return null;}}
 function findVisual(card,text){var stable=activePracticeVisual(card);if(stable)return stable;var n=norm(text),hit=null,count=0;Object.keys(META).forEach(function(s){(META[s]||[]).forEach(function(e){if(e&&e.visual&&norm(e.match)===n){hit=e;count++;}});});return count===1?hit:null;}
-function viewer(v,title){var url=route(v);if(!url)return;var old=document.getElementById('nk-source-viewer');if(old)old.remove();var bd=document.createElement('div');bd.id='nk-source-viewer';bd.innerHTML='<div class="nk-sv-backdrop"><div class="nk-sv-panel"><div class="nk-sv-head"><strong>'+String(title||'Original source visual').replace(/[<>]/g,'')+'</strong><button class="nk-sv-close">×</button></div><div class="nk-sv-stage"><img class="nk-sv-img" draggable="false"></div><div class="nk-sv-controls"><button data-z="-">−</button><button data-z="reset">Reset</button><button data-z="+">+</button></div></div></div>';document.body.appendChild(bd);var img=bd.querySelector('.nk-sv-img'),st=bd.querySelector('.nk-sv-stage');img.src=url;
+function viewer(v,title){var url=route(v);if(!url)return;var old=document.getElementById('nk-source-viewer');if(old)old.remove();var bd=document.createElement('div');bd.id='nk-source-viewer';bd.innerHTML='<div class="nk-sv-backdrop"><div class="nk-sv-panel"><div class="nk-sv-head"><strong>'+String(title||'Original source visual').replace(/[<>]/g,'')+'</strong><button class="nk-sv-close">×</button></div><div class="nk-sv-stage"><img class="nk-sv-img" draggable="false"></div><div class="nk-sv-controls"><button data-z="-">−</button><button data-z="reset">Reset</button><button data-z="+">+</button></div></div></div>';document.body.appendChild(bd);var img=bd.querySelector('.nk-sv-img'),st=bd.querySelector('.nk-sv-stage');img.onload=fit;if(img.complete)fit();img.src=url;
 var scale=1,x=0,y=0,baseScale=1,p=new Map(),gesture=null;
 function clamp(){if(!img.naturalWidth||!img.naturalHeight)return;var iw=img.naturalWidth*scale,ih=img.naturalHeight*scale,sw=st.clientWidth,sh=st.clientHeight;if(iw<=sw)x=(sw-iw)/2;else x=Math.min(0,Math.max(sw-iw,x));if(ih<=sh)y=(sh-ih)/2;else y=Math.min(0,Math.max(sh-ih,y));}
 function apply(){clamp();img.style.transform='translate3d('+x+'px,'+y+'px,0) scale('+scale+')';}
@@ -16,7 +16,7 @@
 function mid(){var a=Array.from(p.values());return{x:(a[0].x+a[1].x)/2,y:(a[0].y+a[1].y)/2};}
 function beginGesture(){if(p.size===1){var a=p.values().next().value;gesture={mode:'pan',sx:a.x,sy:a.y,bx:x,by:y};}else if(p.size===2){var a=Array.from(p.values()),m=mid(),d=Math.hypot(a[0].x-a[1].x,a[0].y-a[1].y);gesture={mode:'pinch',dist:d||1,startScale:scale,anchorX:(m.x-x)/scale,anchorY:(m.y-y)/scale};}}
 function moveGesture(){if(!gesture)return;if(p.size===1&&gesture.mode==='pan'){var a=p.values().next().value;if(scale>baseScale*1.001){x=gesture.bx+a.x-gesture.sx;y=gesture.by+a.y-gesture.sy;apply();}}else if(p.size===2&&gesture.mode==='pinch'){var a=Array.from(p.values()),m=mid(),d=Math.hypot(a[0].x-a[1].x,a[0].y-a[1].y),ns=Math.max(baseScale,Math.min(8,gesture.startScale*d/gesture.dist));scale=ns;x=m.x-gesture.anchorX*ns;y=m.y-gesture.anchorY*ns;apply();}}
-img.onload=fit;bd.querySelector('.nk-sv-close').onclick=function(){bd.remove();};bd.querySelector('[data-z="reset"]').onclick=fit;bd.querySelector('[data-z="+"]').onclick=function(){zoomAt(1.35);};bd.querySelector('[data-z="-"]').onclick=function(){zoomAt(1/1.35);};
+bd.querySelector('.nk-sv-close').onclick=function(){bd.remove();};bd.querySelector('[data-z="reset"]').onclick=fit;bd.querySelector('[data-z="+"]').onclick=function(){zoomAt(1.35);};bd.querySelector('[data-z="-"]').onclick=function(){zoomAt(1/1.35);};
 st.addEventListener('pointerdown',function(e){e.preventDefault();if(st.setPointerCapture)try{st.setPointerCapture(e.pointerId);}catch(_){ }var r=st.getBoundingClientRect();p.set(e.pointerId,{x:e.clientX-r.left,y:e.clientY-r.top});beginGesture();});
 st.addEventListener('pointermove',function(e){if(!p.has(e.pointerId))return;e.preventDefault();var r=st.getBoundingClientRect();p.set(e.pointerId,{x:e.clientX-r.left,y:e.clientY-r.top});moveGesture();});
 ['pointerup','pointercancel','pointerleave'].forEach(function(ev){st.addEventListener(ev,function(e){if(!p.has(e.pointerId))return;p.delete(e.pointerId);if(p.size===0)gesture=null;else beginGesture();});});
```

```diff
--- a/app/src/main/assets/index.html
+++ b/app/src/main/assets/index.html
@@ -1386,7 +1386,7 @@
   let physZoom={scale:1,x:0,y:0,img:null,pointers:new Map(),startDist:0,startScale:1,startX:0,startY:0,baseX:0,baseY:0};
   function applyPhysZoom(){if(physZoom.img)physZoom.img.style.transform=`translate(${physZoom.x}px,${physZoom.y}px) scale(${physZoom.scale})`;}
   function resetPhysZoom(){const i=physZoom.img;if(!i)return;const st=i.parentElement,sx=st.clientWidth/i.naturalWidth,sy=st.clientHeight/i.naturalHeight;physZoom.scale=Math.min(1,Math.min(sx,sy));physZoom.x=(st.clientWidth-i.naturalWidth*physZoom.scale)/2;physZoom.y=(st.clientHeight-i.naturalHeight*physZoom.scale)/2;applyPhysZoom();}
-  function openPhysSourceImage(img){if(!img)return;closePhysSourceImage();const b=document.createElement('div');b.id='phys-zoom-backdrop';b.className='phys-zoom-backdrop';b.innerHTML=`<div class="phys-zoom-toolbar"><div class="phys-zoom-title">Original source · PDF page ${esc(img.getAttribute('data-source-page')||'')}</div><div class="phys-zoom-tools"><button id="pz-minus">−</button><button id="pz-reset">1×</button><button id="pz-plus">+</button><button id="pz-close">×</button></div></div><div class="phys-zoom-stage"><img class="phys-zoom-image" src="${img.src}" alt="${esc(img.alt||'Original source')}"></div>`;document.body.appendChild(b);const st=b.querySelector('.phys-zoom-stage'),i=b.querySelector('.phys-zoom-image');physZoom={scale:1,x:0,y:0,img:i,pointers:new Map(),startDist:0,startScale:1,startX:0,startY:0,baseX:0,baseY:0};i.addEventListener('load',()=>resetPhysZoom());b.querySelector('#pz-close').onclick=closePhysSourceImage;b.querySelector('#pz-reset').onclick=resetPhysZoom;b.querySelector('#pz-plus').onclick=()=>{physZoom.scale=Math.min(5,physZoom.scale*1.35);applyPhysZoom();};b.querySelector('#pz-minus').onclick=()=>{physZoom.scale=Math.max(.5,physZoom.scale/1.35);applyPhysZoom();};st.addEventListener('pointerdown',e=>{st.setPointerCapture?.(e.pointerId);physZoom.pointers.set(e.pointerId,{x:e.clientX,y:e.clientY});if(physZoom.pointers.size===1){physZoom.startX=e.clientX;physZoom.startY=e.clientY;physZoom.baseX=physZoom.x;physZoom.baseY=physZoom.y;}else{const ps=[...physZoom.pointers.values()];physZoom.startDist=Math.hypot(ps[0].x-ps[1].x,ps[0].y-ps[1].y);physZoom.startScale=physZoom.scale;}});st.addEventListener('pointermove',e=>{if(!physZoom.pointers.has(e.pointerId))return;physZoom.pointers.set(e.pointerId,{x:e.clientX,y:e.clientY});const ps=[...physZoom.pointers.values()];if(ps.length===1){physZoom.x=physZoom.baseX+e.clientX-physZoom.startX;physZoom.y=physZoom.baseY+e.clientY-physZoom.startY;applyPhysZoom();}else if(ps.length===2&&physZoom.startDist){const d=Math.hypot(ps[0].x-ps[1].x,ps[0].y-ps[1].y);physZoom.scale=Math.max(.5,Math.min(5,physZoom.startScale*d/physZoom.startDist));applyPhysZoom();}});['pointerup','pointercancel','pointerleave'].forEach(ev=>st.addEventListener(ev,e=>physZoom.pointers.delete(e.pointerId)));b.addEventListener('click',e=>{if(e.target===b)closePhysSourceImage();});}
+  function openPhysSourceImage(img){if(!img)return;closePhysSourceImage();const b=document.createElement('div');b.id='phys-zoom-backdrop';b.className='phys-zoom-backdrop';b.innerHTML=`<div class="phys-zoom-toolbar"><div class="phys-zoom-title">Original source · PDF page ${esc(img.getAttribute('data-source-page')||'')}</div><div class="phys-zoom-tools"><button id="pz-minus">−</button><button id="pz-reset">1×</button><button id="pz-plus">+</button><button id="pz-close">×</button></div></div><div class="phys-zoom-stage"><img class="phys-zoom-image" src="${img.src}" alt="${esc(img.alt||'Original source')}"></div>`;document.body.appendChild(b);const st=b.querySelector('.phys-zoom-stage'),i=b.querySelector('.phys-zoom-image');physZoom={scale:1,x:0,y:0,img:i,pointers:new Map(),startDist:0,startScale:1,startX:0,startY:0,baseX:0,baseY:0};i.addEventListener('load',()=>resetPhysZoom());if(i.complete)resetPhysZoom();b.querySelector('#pz-close').onclick=closePhysSourceImage;b.querySelector('#pz-reset').onclick=resetPhysZoom;b.querySelector('#pz-plus').onclick=()=>{physZoom.scale=Math.min(5,physZoom.scale*1.35);applyPhysZoom();};b.querySelector('#pz-minus').onclick=()=>{physZoom.scale=Math.max(.5,physZoom.scale/1.35);applyPhysZoom();};st.addEventListener('pointerdown',e=>{st.setPointerCapture?.(e.pointerId);physZoom.pointers.set(e.pointerId,{x:e.clientX,y:e.clientY});if(physZoom.pointers.size===1){physZoom.startX=e.clientX;physZoom.startY=e.clientY;physZoom.baseX=physZoom.x;physZoom.baseY=physZoom.y;}else{const ps=[...physZoom.pointers.values()];physZoom.startDist=Math.hypot(ps[0].x-ps[1].x,ps[0].y-ps[1].y);physZoom.startScale=physZoom.scale;}});st.addEventListener('pointermove',e=>{if(!physZoom.pointers.has(e.pointerId))return;physZoom.pointers.set(e.pointerId,{x:e.clientX,y:e.clientY});const ps=[...physZoom.pointers.values()];if(ps.length===1){physZoom.x=physZoom.baseX+e.clientX-physZoom.startX;physZoom.y=physZoom.baseY+e.clientY-physZoom.startY;applyPhysZoom();}else if(ps.length===2&&physZoom.startDist){const d=Math.hypot(ps[0].x-ps[1].x,ps[0].y-ps[1].y);physZoom.scale=Math.max(.5,Math.min(5,physZoom.startScale*d/physZoom.startDist));applyPhysZoom();}});['pointerup','pointercancel','pointerleave'].forEach(ev=>st.addEventListener(ev,e=>physZoom.pointers.delete(e.pointerId)));b.addEventListener('click',e=>{if(e.target===b)closePhysSourceImage();});}
   function closePhysSourceImage(){document.getElementById('phys-zoom-backdrop')?.remove();physZoom={scale:1,x:0,y:0,img:null,pointers:new Map(),startDist:0,startScale:1,startX:0,startY:0,baseX:0,baseY:0};}
   window.openPhysSourceImage=openPhysSourceImage;window.closePhysSourceImage=closePhysSourceImage;
 
```
(The `src` is set via `innerHTML` before the listener; moving listener attachment before `innerHTML` parse is not possible, so the `complete` check covers the cached case.)

## Verification

- Open a source figure twice in succession; the second open (cached) should still be fitted to the stage / centered.
- Manual: throttle network and open twice; confirm no stuck intrinsic-size image.

## Alternatives considered

Forcing `loading="eager"` does not help because the race is about listener timing, not fetch priority.

## Main-agent review

- **Verdict:** approved
- **Checked patch:** yes
- **Checked evidence:** yes
- **Notes:** The finding is correct and both hunks are right.

Verified both viewers. `source_visual_renderer.js:10` set `img.src=url` and only attached `img.onload=fit` at line 19, after the whole handler body; the Physiology viewer in `index.html:1389` built its `<img src="...">` through `innerHTML` and attached the `load` listener after `document.body.appendChild(b)`. In both, a cache hit can deliver `load` before the handler exists.

The patch attaches the handler before the source is set and adds an explicit `if (complete)` call, so the image is fitted whether the event has already fired or fires later.

`tools/test_source_visual_viewer_v1.py` is new. It runs the shipped `source_visual_renderer.js` against a fake DOM whose image fires `load` synchronously when `src` is set, which is what a cache hit looks like from the renderer's side, and asserts the zoom transform was applied. On the pre-fix renderer the assertion fails with "a cached image was never fitted: no zoom transform was applied". The Physiology viewer, which lives in the page rather than in a module, is checked against the page source for the same `if(i.complete)resetPhysZoom();` guard.
