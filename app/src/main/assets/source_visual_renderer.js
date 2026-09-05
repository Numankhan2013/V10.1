/* NK QBank V11 — source visual renderer
 * Injected at build time so the trusted V10.3.11 shell remains untouched.
 * Metadata is text-keyed: no question-number heuristics.
 */
(function(){
  'use strict';
  if (window.__NK_SOURCE_VISUALS__) return;
  window.__NK_SOURCE_VISUALS__ = true;

  var META = window.SOURCE_VISUALS || {};
  var mounted = new WeakSet();
  var SUBJECT_ALIASES = { anatomy:'Anatomy', physiology:'Physiology', biochemistry:'Biochemistry' };

  function norm(s){
    return String(s||'').toLowerCase().replace(/\s+/g,' ').replace(/[^a-z0-9%°μ×÷+\-./ ]/g,'').trim();
  }
  function words(s){ return norm(s).split(' ').filter(function(x){return x.length>2;}); }
  function score(a,b){
    var aa=words(a), bb=words(b); if(!aa.length||!bb.length) return 0;
    var set={}; aa.forEach(function(x){set[x]=1;});
    var hit=0; bb.forEach(function(x){if(set[x])hit++;});
    return hit/Math.max(6,Math.min(aa.length,bb.length));
  }
  function currentSubject(){
    var body=(document.body&&document.body.innerText||'').slice(0,1200).toLowerCase();
    if(/\banatomy\b/.test(body)) return 'Anatomy';
    if(/\bphysiology\b/.test(body)) return 'Physiology';
    return 'Biochemistry';
  }
  function entriesFor(subject){ return (META[subject]||[]); }
  function findVisual(subject, text){
    var exact=norm(text), list=entriesFor(subject), best=null, bs=0;
    if(!exact) return null;
    for(var i=0;i<list.length;i++){
      var e=list[i], m=norm(e.match||e.question||'');
      if(!m) continue;
      if(m===exact) return e;
      var sc=score(exact,m);
      if(sc>bs){bs=sc;best=e;}
    }
    return bs>=0.55 ? best : null;
  }
  function route(v){
    if(!v || v.type!=='source-pdf' || !v.source || !v.page) return null;
    var subject=(v.subject||'').toLowerCase();
    var path=subject==='anatomy'?'anatomy':subject==='physiology'?'physiology':'biochemistry';
    var q=['page='+encodeURIComponent(v.page),'scale='+encodeURIComponent(v.scale||2.5)];
    if(v.crop){ ['top','bottom','left','right'].forEach(function(k){if(v.crop[k]!=null)q.push(k+'='+encodeURIComponent(v.crop[k]));}); }
    return 'https://qbank.local/'+path+'/pdf?'+q.join('&');
  }
  function viewer(v,title){
    var url=route(v); if(!url)return;
    var old=document.getElementById('nk-source-viewer'); if(old)old.remove();
    var bd=document.createElement('div'); bd.id='nk-source-viewer';
    bd.innerHTML='<div class="nk-sv-backdrop"><div class="nk-sv-panel" role="dialog" aria-label="Source visual"><div class="nk-sv-head"><strong>'+escapeHtml(title||'Source visual')+'</strong><button class="nk-sv-close" aria-label="Close">×</button></div><div class="nk-sv-stage"><img class="nk-sv-img" draggable="false" alt="Source visual"></div><div class="nk-sv-controls"><button data-z="-">−</button><button data-z="reset">Reset</button><button data-z="+">+</button></div></div></div>';
    document.body.appendChild(bd);
    var img=bd.querySelector('.nk-sv-img'), stage=bd.querySelector('.nk-sv-stage');
    var scale=1, min=1, max=5, x=0, y=0, sx=0, sy=0, dragging=false;
    img.src=url;
    function apply(){img.style.transform='translate3d('+x+'px,'+y+'px,0) scale('+scale+')';}
    function reset(){scale=1;x=0;y=0;apply();}
    function zoom(d){scale=Math.max(min,Math.min(max,scale+d));apply();}
    bd.querySelector('.nk-sv-close').onclick=function(){bd.remove();};
    bd.querySelectorAll('[data-z]').forEach(function(b){b.onclick=function(){var z=b.getAttribute('data-z');z==='+'?zoom(.5):z==='-'?zoom(-.5):reset();};});
    stage.addEventListener('wheel',function(e){e.preventDefault();zoom(e.deltaY<0?.25:-.25);},{passive:false});
    stage.addEventListener('dblclick',function(){scale=scale>1?1:2;apply();});
    stage.addEventListener('pointerdown',function(e){if(scale<=1)return;dragging=true;sx=e.clientX-x;sy=e.clientY-y;stage.setPointerCapture(e.pointerId);});
    stage.addEventListener('pointermove',function(e){if(!dragging)return;x=e.clientX-sx;y=e.clientY-sy;apply();});
    stage.addEventListener('pointerup',function(){dragging=false;});
    stage.addEventListener('pointercancel',function(){dragging=false;});
    bd.addEventListener('click',function(e){if(e.target===bd.querySelector('.nk-sv-backdrop'))bd.remove();});
    apply();
  }
  function escapeHtml(s){return String(s||'').replace(/[&<>\"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;',"'":'&#39;'}[c];});}
  function addVisual(host,v,label){
    if(!v || host.querySelector(':scope > .nk-source-visual'))return;
    var wrap=document.createElement('div'); wrap.className='nk-source-visual';
    var img=document.createElement('img'); img.alt=label||'Question visual'; img.loading='eager'; img.src=route(v);
    wrap.appendChild(img);
    wrap.onclick=function(){viewer(v,label||'Source visual');};
    host.appendChild(wrap);
  }
  function mount(){
    var subject=currentSubject();
    document.querySelectorAll('.question-card').forEach(function(card){
      if(mounted.has(card))return;
      var qt=card.querySelector('.question-text'); if(!qt)return;
      var visual=findVisual(subject,qt.textContent||'');
      if(visual && visual.visual){
        addVisual(qt.parentElement||card,visual.visual,'Question visual');
      }
      card.querySelectorAll('.option').forEach(function(opt){
        var ot=opt.querySelector('.option-text'); if(!ot)return;
        var ov=findVisual(subject,(ot.textContent||''));
        if(ov && ov.option) addVisual(opt,ov.option,'Option visual');
      });
      mounted.add(card);
    });
  }
  var css=document.createElement('style'); css.textContent='.nk-source-visual{margin:10px 0 16px;border:1px solid var(--line,#e7e8ee);border-radius:14px;overflow:hidden;background:#f7f7f9;cursor:zoom-in;box-shadow:0 5px 16px rgba(32,34,58,.05)}.nk-source-visual img{display:block;width:100%;height:auto;max-height:520px;object-fit:contain}.nk-sv-backdrop{position:fixed;inset:0;z-index:1000;background:rgba(15,16,28,.88);display:grid;place-items:center;padding:12px}.nk-sv-panel{width:min(1000px,100%);height:min(94vh,900px);display:flex;flex-direction:column;background:#10111b;border:1px solid rgba(255,255,255,.14);border-radius:18px;overflow:hidden;box-shadow:0 28px 90px rgba(0,0,0,.45)}.nk-sv-head{display:flex;align-items:center;justify-content:space-between;color:white;padding:11px 14px;background:rgba(255,255,255,.06)}.nk-sv-close{border:0;background:transparent;color:white;font-size:27px;width:38px;height:38px;border-radius:10px}.nk-sv-stage{flex:1;min-height:0;display:grid;place-items:center;overflow:hidden;touch-action:none;background:#090a10}.nk-sv-img{max-width:100%;max-height:100%;object-fit:contain;transform-origin:center center;user-select:none}.nk-sv-controls{display:flex;justify-content:center;gap:8px;padding:10px;background:rgba(255,255,255,.06)}.nk-sv-controls button{min-width:74px;border:1px solid rgba(255,255,255,.16);border-radius:10px;padding:8px 12px;background:rgba(255,255,255,.08);color:white;font-weight:700}'; document.head.appendChild(css);
  var obs=new MutationObserver(function(){mount();});
  obs.observe(document.documentElement,{childList:true,subtree:true});
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',mount);else mount();
})();
