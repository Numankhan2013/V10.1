from pathlib import Path

INDEX = Path('app/src/main/assets/index.html')
MARKER = 'id="v102-next-ui"'

CSS = r'''<style id="v102-next-ui">
:root{--v102-brand:#5146df;--v102-ink:#151827;--v102-muted:#6b7285;--v102-line:#dfe4ec;--v102-soft:#f5f7fb;--v102-success:#0f9d78;--v102-success-bg:#e4f8f0;--v102-danger:#d94950;--v102-danger-bg:#fde9eb;--v102-shadow:0 10px 28px rgba(23,29,61,.08)}
html,body{background:var(--v102-soft);-webkit-font-smoothing:antialiased;text-rendering:optimizeLegibility}
.topbar .icon-btn{display:none!important}.topbar.v102-topbar{justify-content:center;min-height:64px;background:linear-gradient(135deg,#1e1b4b 0%,#312e81 58%,#5146df 100%);box-shadow:0 6px 22px rgba(39,35,94,.18)}
.topbar.v102-topbar .brand{font-weight:850;letter-spacing:-.25px}.topbar.v102-topbar .brand-mark{width:36px;height:36px;border-radius:11px;box-shadow:0 8px 20px rgba(0,0,0,.18),inset 0 0 0 1px rgba(255,255,255,.18)}
.v102-subject-hub{margin:0 0 16px;padding:18px;border:1px solid rgba(43,49,80,.07);border-radius:22px;background:linear-gradient(145deg,#fff 0%,#f8f9ff 100%);box-shadow:var(--v102-shadow)}
.v102-section-head{display:flex;align-items:flex-end;justify-content:space-between;gap:14px;margin-bottom:12px}.v102-section-head h2{margin:3px 0 0;font-size:22px;line-height:1.12;letter-spacing:-.65px;font-weight:900;color:var(--v102-ink)}.v102-section-head>span{font-size:11px;font-weight:750;color:var(--v102-muted)}
.v102-eyebrow{font-size:10px;font-weight:900;letter-spacing:1px;text-transform:uppercase;color:var(--v102-brand)}
.v102-subject-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px}.v102-subject-card{min-width:0;display:flex;align-items:center;gap:11px;padding:14px 13px;text-align:left;border:1px solid var(--v102-line);border-radius:17px;background:#fff;color:var(--v102-ink);box-shadow:0 3px 10px rgba(23,29,61,.03);transition:transform .12s ease,border-color .12s ease,box-shadow .12s ease,background .12s ease}.v102-subject-card:hover{transform:translateY(-1px);border-color:#b8bde3;box-shadow:0 9px 20px rgba(23,29,61,.07)}.v102-subject-card.is-active{background:linear-gradient(145deg,#f0efff,#fff);border-color:#aaa5e8;box-shadow:0 9px 22px rgba(81,70,223,.11)}
.v102-subject-mark{width:42px;height:42px;display:grid;place-items:center;flex:none;border-radius:13px;background:linear-gradient(135deg,#eeeaff,#e7efff);color:var(--v102-brand);font-size:13px;font-weight:900;letter-spacing:.5px}.v102-subject-copy{display:grid;gap:4px;min-width:0;flex:1}.v102-subject-copy strong{font-size:14px;font-weight:850;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.v102-subject-copy small{font-size:10px;color:var(--v102-muted);line-height:1.3}.v102-subject-arrow{font-size:24px;color:#a1a5b4;line-height:1}.v102-subject-hint{margin:11px 2px 0;color:var(--v102-muted);font-size:11px;line-height:1.45}
.v102-topic-modal{position:fixed;inset:0;z-index:95;background:rgba(22,23,38,.46);backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px);display:grid;place-items:end center;padding:14px}.v102-topic-dialog{width:min(720px,100%);max-height:min(82vh,760px);overflow:auto;background:#fff;border-radius:24px;padding:18px;box-shadow:0 30px 90px rgba(0,0,0,.24)}.v102-topic-head{display:flex;align-items:flex-start;justify-content:space-between;gap:12px;margin-bottom:13px}.v102-topic-head h3{margin:2px 0 4px;font-size:22px;line-height:1.12;font-weight:900;letter-spacing:-.6px}.v102-topic-head p{margin:0;color:var(--v102-muted);font-size:12px}.v102-topic-close{width:44px;height:44px;border:1px solid var(--v102-line);border-radius:13px;background:#fff;font-size:22px;color:#606577}.v102-topic-list{display:grid;gap:8px}.v102-topic-item{display:flex;align-items:center;gap:10px;width:100%;padding:13px 14px;text-align:left;border:1px solid var(--v102-line);background:#fff;border-radius:15px}.v102-topic-item:hover{border-color:#b9bde2;background:#fafaff}.v102-topic-num{width:30px;height:30px;display:grid;place-items:center;flex:none;border-radius:10px;background:#f0f1f7;color:#646a7a;font-size:10px;font-weight:850}.v102-topic-title{flex:1;font-size:13px;font-weight:780;line-height:1.35;color:var(--v102-ink)}.v102-topic-arrow{font-size:20px;color:#9aa0ae}
.question-text{font-size:18px;line-height:1.62;font-weight:675;letter-spacing:-.16px;color:#161a2b}.option-list{gap:12px}.option{position:relative;min-height:72px;display:flex;align-items:flex-start;gap:14px;padding:17px 18px;border:1.5px solid #dfe4ec!important;border-radius:18px!important;background:#fff;box-shadow:0 2px 8px rgba(24,30,58,.025);transition:transform .12s ease,border-color .12s ease,background .12s ease,box-shadow .12s ease}.option:hover{transform:translateY(-1px);border-color:#bec5d5!important;background:#fff;box-shadow:0 8px 20px rgba(24,30,58,.065)}.option-text{font-size:16px;line-height:1.58;font-weight:560;color:#272c3b;overflow-wrap:anywhere;max-width:calc(100% - 6px)}.option-letter{font-size:14px;font-weight:900;width:22px;padding-top:3px;color:#626a7a}.radio{width:27px;height:27px;border-width:1.8px;margin-top:0}
.option.selected{background:#eef2ff!important;border-color:#7383de!important;box-shadow:0 8px 20px rgba(61,101,216,.09)!important}.option.correct,.option.correct.selected{background:var(--v102-success-bg)!important;border-color:#55bc9e!important;box-shadow:0 10px 28px rgba(15,157,120,.13)!important}.option.wrong,.option.wrong.selected{background:var(--v102-danger-bg)!important;border-color:#e38a90!important;box-shadow:0 10px 28px rgba(217,73,80,.11)!important}
.option.correct:after,.option.wrong:after{position:absolute;right:16px;top:14px;display:grid;place-items:center;width:29px;height:29px;border-radius:50%;font-weight:950;font-size:17px;background:rgba(255,255,255,.62)}.option.correct:after{content:"✓";color:var(--v102-success);border:1px solid #91dbc5}.option.wrong:after{content:"×";color:var(--v102-danger);border:1px solid #efb4b8}.option.correct .radio{border-color:var(--v102-success)}.option.correct .radio:after{content:"✓";font-size:16px;color:var(--v102-success);font-weight:950}.option.wrong .radio{border-color:var(--v102-danger)}.option.wrong .radio:after{content:"×";font-size:17px;color:var(--v102-danger);font-weight:950}
.feedback{margin-top:17px;padding:18px 18px 20px;border-radius:20px;box-shadow:0 8px 24px rgba(25,31,60,.045)}.feedback.good{background:linear-gradient(145deg,#f1fcf7,#fff);border-color:#b8e4d6}.feedback.bad{background:linear-gradient(145deg,#fff5f6,#fff);border-color:#efc5c8}.feedback-title{font-size:16px;font-weight:900;letter-spacing:-.2px;margin-bottom:9px}.feedback-body{font-size:15px;line-height:1.72;color:#3c4352;white-space:normal;overflow-wrap:anywhere;max-width:78ch}.feedback-body p{margin:0 0 13px}.feedback-body p:last-child{margin-bottom:0}.feedback-body ul{margin:7px 0 13px 21px;padding:0}.feedback-body li{margin:0 0 7px;padding-left:2px}.v102-explanation-heading{margin:18px 0 7px;font-size:13px;line-height:1.25;font-weight:900;letter-spacing:.25px;color:#2b3050;text-transform:uppercase}.v102-explanation-option{display:grid;grid-template-columns:72px 1fr;gap:10px;padding:9px 0;border-top:1px solid #e7e9ef}.v102-explanation-option>strong{font-size:12px;font-weight:900;color:#6a7181}.v102-explanation-option>span{font-size:14px;line-height:1.58;color:#363d4d}
.source-box{border-radius:17px;background:#fbfbfe}.source-box summary{font-size:13px}.source-preview{max-width:100%;overflow:auto}.v102-review-action{min-height:50px;padding-left:18px;padding-right:18px}.result-hero{border-radius:24px;box-shadow:var(--v102-shadow)}
@media(max-width:800px){.v102-subject-grid{grid-template-columns:1fr 1fr}.v102-topic-dialog{max-height:86vh}}@media(max-width:640px){.v102-subject-hub{padding:16px;border-radius:20px}.v102-subject-grid{grid-template-columns:1fr}.v102-subject-card{padding:14px}.question-text{font-size:18px;line-height:1.62}.option{min-height:76px;padding:18px 16px}.option-text{font-size:16px;line-height:1.6;padding-right:28px}.option-letter{width:21px}.radio{width:28px;height:28px}.option.correct:after,.option.wrong:after{right:10px;top:11px}.feedback{padding:17px}.feedback-body{font-size:15px;line-height:1.74}.v102-topic-dialog{padding:16px;border-radius:22px}.v102-topic-item{min-height:54px}}@media(prefers-reduced-motion:reduce){*,*::before,*::after{scroll-behavior:auto!important;transition:none!important;animation:none!important}}
</style>'''

JS = r'''<script id="v102-next-ui-behavior">
(function(){
  'use strict';
  const esc=v=>String(v==null?'':v).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const closeTopics=()=>document.getElementById('v102-topic-modal')?.remove();
  function topicSource(subject){
    if(subject==='Biochemistry'&&window.QBANK_DATA&&Array.isArray(window.QBANK_DATA.chapters)) return window.QBANK_DATA.chapters;
    const list=window.SUBJECT_QBANK_DATA&&Array.isArray(window.SUBJECT_QBANK_DATA.subjects)?window.SUBJECT_QBANK_DATA.subjects:[];
    const found=list.find(x=>x&&x.subject===subject); return found&&Array.isArray(found.topics)?found.topics:[];
  }
  function openTopics(subject){
    closeTopics(); const topics=topicSource(subject);
    const html=topics.map((t,i)=>{const id=t.id!=null?t.id:(t.chapterId!=null?t.chapterId:i+1),title=t.title||t.name||`Topic ${i+1}`,count=t.questionCount!=null?t.questionCount:(Array.isArray(t.questions)?t.questions.length:'');return `<button type="button" class="v102-topic-item" data-v102-topic="1" data-topic-id="${esc(id)}"><span class="v102-topic-num">${String(i+1).padStart(2,'0')}</span><span class="v102-topic-title">${esc(title)}${count!==''?`<small style="display:block;color:#747b8b;font-size:10px;margin-top:3px">${esc(count)} questions</small>`:''}</span><span class="v102-topic-arrow">›</span></button>`;}).join('');
    document.body.insertAdjacentHTML('beforeend',`<div class="v102-topic-modal" id="v102-topic-modal" role="dialog" aria-modal="true"><div class="v102-topic-dialog"><div class="v102-topic-head"><div><div class="v102-eyebrow">${esc(subject)}</div><h3>Choose a topic</h3><p>${topics.length} topics available</p></div><button type="button" class="v102-topic-close" id="v102-topic-modal-close" aria-label="Close">×</button></div><div class="v102-topic-list">${html||'<div class="empty"><strong>No topics found</strong><span>Use the Topics tab to browse this subject.</span></div>'}</div></div></div>`);
  }
  function mountSubjectHub(){
    const strip=document.querySelector('.subject-strip'); if(!strip||strip.dataset.v102Mounted==='1') return;
    const select=strip.querySelector('select.subject-switch'); if(!select) return;
    const opts=[...select.options].map(o=>({name:o.textContent.trim(),value:o.value,active:o.selected}));
    strip.dataset.v102Mounted='1';
    strip.outerHTML=`<section class="v102-subject-hub" aria-labelledby="v102-subject-title"><div class="v102-section-head"><div><div class="v102-eyebrow">Study library</div><h2 id="v102-subject-title">Choose a subject</h2></div><span>${opts.length} subjects</span></div><div class="v102-subject-grid">${opts.map(x=>`<button type="button" class="v102-subject-card ${x.active?'is-active':''}" data-v102-subject="${esc(x.value)}" aria-pressed="${x.active?'true':'false'}"><span class="v102-subject-mark">${esc(x.name.slice(0,2).toUpperCase())}</span><span class="v102-subject-copy"><strong>${esc(x.name)}</strong><small>Open topics and start practice</small></span><span class="v102-subject-arrow">›</span></button>`).join('')}</div><p class="v102-subject-hint">Choose a subject first, then select a topic.</p></section>`;
  }
  function formatExplanations(){
    document.querySelectorAll('.feedback-body').forEach(el=>{
      if(el.dataset.v102Formatted==='1'||el.children.length)return;
      const raw=(el.textContent||'').replace(/\r/g,'').trim(); if(raw.length<120)return;
      const lines=raw.split('\n').map(x=>x.trim()).filter(Boolean),out=[]; let para=[],bullets=[];
      const flushP=()=>{if(para.length){out.push(`<p>${esc(para.join(' '))}</p>`);para=[];}}; const flushB=()=>{if(bullets.length){out.push(`<ul>${bullets.map(x=>`<li>${esc(x)}</li>`).join('')}</ul>`);bullets=[];}};
      const heading=/^(explanation|why|mechanism|key concept|key point|clinical features|diagnosis|investigations|treatment|pathophysiology|algorithm|other options|summary|important|note|features|functions|complications|source explanation|solution for question)\s*:?[ \t]*$/i; const opt=/^option\s*([a-d])\s*[:.)-]\s*(.*)$/i;
      lines.forEach(line=>{if(/^•\s*/.test(line)){flushP();bullets.push(line.replace(/^•\s*/,''));return;}const h=line.match(heading);if(h){flushP();flushB();out.push(`<div class="v102-explanation-heading">${esc(h[1])}</div>`);return;}const o=line.match(opt);if(o){flushP();flushB();out.push(`<div class="v102-explanation-option"><strong>Option ${esc(o[1].toUpperCase())}</strong><span>${esc(o[2])}</span></div>`);return;}para.push(line);});
      flushP();flushB(); if(out.length){el.innerHTML=out.join('');el.dataset.v102Formatted='1';}
    });
  }
  document.addEventListener('click',function(e){
    const card=e.target?.closest?.('[data-v102-subject]');
    if(card){e.preventDefault();e.stopPropagation();const name=card.getAttribute('data-v102-subject')||'';const select=document.querySelector('select.subject-switch');if(select){select.value=name;select.dispatchEvent(new Event('change',{bubbles:true}));}setTimeout(()=>openTopics(name),35);return;}
    const topic=e.target?.closest?.('[data-v102-topic]');
    if(topic){e.preventDefault();e.stopPropagation();const id=topic.getAttribute('data-topic-id');closeTopics();setTimeout(()=>window.QB&&typeof window.QB.openChapter==='function'&&window.QB.openChapter(id),0);return;}
    if(e.target?.id==='v102-topic-modal'||e.target?.id==='v102-topic-modal-close'){closeTopics();return;}
    const review=e.target?.closest?.('[data-v102-review-cta]');
    if(review){e.preventDefault();e.stopPropagation();if(e.stopImmediatePropagation)e.stopImmediatePropagation();const id=review.getAttribute('data-review-test-id');if(!id)return;const go=()=>{try{if(window.QB&&typeof window.QB.reviewTest==='function'){window.QB.reviewTest(id);return true;}}catch(_){ }return false;};if(!go())[0,25,100,250].forEach(ms=>setTimeout(go,ms));}
  },true);
  const mo=new MutationObserver(()=>{mountSubjectHub();formatExplanations();});mo.observe(document.body,{subtree:true,childList:true});
  const boot=()=>{mountSubjectHub();formatExplanations();}; if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',boot);else boot(); [50,250,800].forEach(ms=>setTimeout(boot,ms));
})();
</script>'''


def main():
    s=INDEX.read_text(encoding='utf-8')
    if MARKER in s:
        print('V10.2 UI layer already present; no changes made.'); return
    if '</body>' not in s: raise SystemExit('No </body> marker found in index.html')
    INDEX.write_text(s.replace('</body>',CSS+'\n'+JS+'\n</body>',1),encoding='utf-8')
    print('Applied V10.2 immersive UI + review reliability layer')

if __name__=='__main__':
    main()
