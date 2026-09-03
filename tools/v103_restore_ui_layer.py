from pathlib import Path

p = Path('app/src/main/assets/index.html')
s = p.read_text(encoding='utf-8')

if 'id="v102-next-ui"' not in s:
    css = r'''<style id="v102-next-ui">
:root{--v102-brand:#5146df;--v102-ink:#151827;--v102-muted:#6b7285;--v102-line:#dfe4ec;--v102-soft:#f5f7fb;--v102-success:#0f9d78;--v102-success-bg:#e4f8f0;--v102-danger:#d94950;--v102-danger-bg:#fde9eb;--v102-shadow:0 10px 28px rgba(23,29,61,.08)}
html,body{background:var(--v102-soft);-webkit-font-smoothing:antialiased;text-rendering:optimizeLegibility}
.topbar .icon-btn{display:none!important}.topbar.v102-topbar{justify-content:center;min-height:64px;background:linear-gradient(135deg,#1e1b4b 0%,#312e81 58%,#5146df 100%);box-shadow:0 6px 22px rgba(39,35,94,.18)}
.topbar.v102-topbar .brand{font-weight:850;letter-spacing:-.25px}.topbar.v102-topbar .brand-mark{width:36px;height:36px;border-radius:11px}
.v102-subject-hub{margin:0 0 16px;padding:18px;border:1px solid rgba(43,49,80,.07);border-radius:22px;background:linear-gradient(145deg,#fff 0%,#f8f9ff 100%);box-shadow:var(--v102-shadow)}
.v102-section-head{display:flex;align-items:flex-end;justify-content:space-between;gap:14px;margin-bottom:12px}.v102-section-head h2{margin:3px 0 0;font-size:22px;line-height:1.12;font-weight:900;color:var(--v102-ink)}.v102-section-head>span{font-size:11px;font-weight:750;color:var(--v102-muted)}
.v102-eyebrow{font-size:10px;font-weight:900;letter-spacing:1px;text-transform:uppercase;color:var(--v102-brand)}
.v102-subject-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px}.v102-subject-card{min-width:0;display:flex;align-items:center;gap:11px;padding:14px 13px;text-align:left;border:1px solid var(--v102-line);border-radius:17px;background:#fff;color:var(--v102-ink)}.v102-subject-card.is-active{background:linear-gradient(145deg,#f0efff,#fff);border-color:#aaa5e8}.v102-subject-mark{width:42px;height:42px;display:grid;place-items:center;flex:none;border-radius:13px;background:linear-gradient(135deg,#eeeaff,#e7efff);color:var(--v102-brand);font-size:13px;font-weight:900}.v102-subject-copy{display:grid;gap:4px;min-width:0;flex:1}.v102-subject-copy strong{font-size:14px;font-weight:850;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.v102-subject-copy small{font-size:10px;color:var(--v102-muted)}.v102-subject-arrow{font-size:24px;color:#a1a5b4}.v102-subject-hint{margin:11px 2px 0;color:var(--v102-muted);font-size:11px}
.v102-topic-modal{position:fixed;inset:0;z-index:95;background:rgba(22,23,38,.46);backdrop-filter:blur(8px);display:grid;place-items:end center;padding:14px}.v102-topic-dialog{width:min(720px,100%);max-height:min(82vh,760px);overflow:auto;background:#fff;border-radius:24px;padding:18px;box-shadow:0 30px 90px rgba(0,0,0,.24)}.v102-topic-head{display:flex;align-items:flex-start;justify-content:space-between;gap:12px;margin-bottom:13px}.v102-topic-head h3{margin:2px 0 4px;font-size:22px;font-weight:900}.v102-topic-head p{margin:0;color:var(--v102-muted);font-size:12px}.v102-topic-close{width:44px;height:44px;border:1px solid var(--v102-line);border-radius:13px;background:#fff;font-size:22px;color:#606577}.v102-topic-list{display:grid;gap:8px}.v102-topic-item{display:flex;align-items:center;gap:10px;width:100%;padding:13px 14px;text-align:left;border:1px solid var(--v102-line);background:#fff;border-radius:15px}.v102-topic-num{width:30px;height:30px;display:grid;place-items:center;flex:none;border-radius:10px;background:#f0f1f7;color:#646a7a;font-size:10px;font-weight:850}.v102-topic-title{flex:1;font-size:13px;font-weight:780;line-height:1.35;color:var(--v102-ink)}.v102-topic-arrow{font-size:20px;color:#9aa0ae}
.question-text{font-size:18px;line-height:1.62;font-weight:675;color:#161a2b}.option-list{gap:12px}.option{position:relative;min-height:72px;display:flex;align-items:flex-start;gap:14px;padding:17px 18px;border:1.5px solid #dfe4ec!important;border-radius:18px!important;background:#fff;box-shadow:0 2px 8px rgba(24,30,58,.025)}.option-text{font-size:16px;line-height:1.58;font-weight:560;color:#272c3b;overflow-wrap:anywhere;max-width:calc(100% - 6px)}.option-letter{font-size:14px;font-weight:900;width:22px;padding-top:3px;color:#626a7a}.radio{width:27px;height:27px;border-width:1.8px;margin-top:0}.option.selected{background:#eef2ff!important;border-color:#7383de!important}.option.correct,.option.correct.selected{background:var(--v102-success-bg)!important;border-color:#55bc9e!important;box-shadow:0 10px 28px rgba(15,157,120,.13)!important}.option.wrong,.option.wrong.selected{background:var(--v102-danger-bg)!important;border-color:#e38a90!important;box-shadow:0 10px 28px rgba(217,73,80,.11)!important}.feedback{margin-top:17px;padding:18px;border-radius:20px}.feedback-title{font-size:16px;font-weight:900}.feedback-body{font-size:15px;line-height:1.72;color:#3c4352;white-space:normal;overflow-wrap:anywhere;max-width:78ch}.v102-explanation-heading{margin:18px 0 7px;font-size:13px;font-weight:900;color:#2b3050;text-transform:uppercase}.v102-explanation-option{display:grid;grid-template-columns:72px 1fr;gap:10px;padding:9px 0;border-top:1px solid #e7e9ef}.v102-review-action{min-height:50px;padding-left:18px;padding-right:18px}.result-hero{border-radius:24px;box-shadow:var(--v102-shadow)}
@media(max-width:800px){.v102-subject-grid{grid-template-columns:1fr 1fr}}@media(max-width:640px){.v102-subject-grid{grid-template-columns:1fr}.v102-subject-card{padding:14px}.question-text{font-size:18px}.option{min-height:76px;padding:18px 16px}.option-text{font-size:16px;line-height:1.6;padding-right:28px}.feedback-body{font-size:15px;line-height:1.74}.v102-topic-dialog{padding:16px}}
</style>'''
    s = s.replace('</head>', css + '</head>', 1)

if 'id="v102-next-ui-behavior"' not in s:
    js = r'''<script id="v102-next-ui-behavior">
(function(){
'use strict';
const esc=v=>String(v==null?'':v).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function topicSource(subject){
 if(subject==='Biochemistry'&&window.QBANK_DATA&&Array.isArray(window.QBANK_DATA.chapters))return window.QBANK_DATA.chapters;
 const list=window.SUBJECT_QBANK_DATA&&Array.isArray(window.SUBJECT_QBANK_DATA.subjects)?window.SUBJECT_QBANK_DATA.subjects:[];
 const found=list.find(x=>x&&x.subject===subject);return found&&Array.isArray(found.topics)?found.topics:[];
}
function closeTopics(){document.getElementById('v102-topic-modal')?.remove();}
function openTopics(subject){
 closeTopics();const topics=topicSource(subject);const html=topics.map((t,i)=>{const id=t.id!=null?t.id:(t.chapterId!=null?t.chapterId:i+1),title=t.title||t.name||`Topic ${i+1}`,count=t.questionCount!=null?t.questionCount:(Array.isArray(t.questions)?t.questions.length:'');return `<button type="button" class="v102-topic-item" data-v102-topic="1" data-topic-id="${esc(id)}"><span class="v102-topic-num">${String(i+1).padStart(2,'0')}</span><span class="v102-topic-title">${esc(title)}${count!==''?`<small style="display:block;color:#747b8b;font-size:10px;margin-top:3px">${esc(count)} questions</small>`:''}</span><span class="v102-topic-arrow">›</span></button>`}).join('');
 document.body.insertAdjacentHTML('beforeend',`<div class="v102-topic-modal" id="v102-topic-modal" role="dialog" aria-modal="true"><div class="v102-topic-dialog"><div class="v102-topic-head"><div><div class="v102-eyebrow">${esc(subject)}</div><h3>Choose a topic</h3><p>${topics.length} topics available</p></div><button type="button" class="v102-topic-close" id="v102-topic-modal-close" aria-label="Close">×</button></div><div class="v102-topic-list">${html||'<div class="empty"><strong>No topics found</strong></div>'}</div></div></div>`);
}
function mountSubjectHub(){
 const strip=document.querySelector('.subject-strip');if(!strip||strip.dataset.v102Mounted==='1')return;const select=strip.querySelector('select.subject-switch');if(!select)return;
 const opts=[...select.options].map(o=>({name:o.textContent.trim(),value:o.value,active:o.selected}));strip.dataset.v102Mounted='1';
 strip.outerHTML=`<section class="v102-subject-hub" aria-labelledby="v102-subject-title"><div class="v102-section-head"><div><div class="v102-eyebrow">Study library</div><h2 id="v102-subject-title">Choose a subject</h2></div><span>${opts.length} subjects</span></div><div class="v102-subject-grid">${opts.map(x=>`<button type="button" class="v102-subject-card ${x.active?'is-active':''}" data-v102-subject="${esc(x.value)}" aria-pressed="${x.active?'true':'false'}"><span class="v102-subject-mark">${esc(x.name.slice(0,2).toUpperCase())}</span><span class="v102-subject-copy"><strong>${esc(x.name)}</strong><small>Open topics and start practice</small></span><span class="v102-subject-arrow">›</span></button>`).join('')}</div><p class="v102-subject-hint">Choose a subject first, then select a topic.</p></section>`;
}
function wireClicks(){
 document.addEventListener('click',e=>{
  const sub=e.target.closest('[data-v102-subject]');if(sub){openTopics(sub.getAttribute('data-v102-subject'));return;}
  if(e.target.closest('#v102-topic-modal-close')||e.target.id==='v102-topic-modal'){closeTopics();return;}
  const topic=e.target.closest('[data-v102-topic]');if(topic){closeTopics();const id=topic.getAttribute('data-topic-id');if(window.QB&&typeof window.QB.startTopic==='function')window.QB.startTopic(id);else if(window.QB&&typeof window.QB.openTopic==='function')window.QB.openTopic(id);return;}
 });
}
function formatExplanations(){
 document.querySelectorAll('.feedback-body').forEach(el=>{if(el.dataset.v102Formatted==='1'||el.children.length)return;const raw=(el.textContent||'').replace(/\r/g,'').trim();if(raw.length<120)return;const lines=raw.split('\n').map(x=>x.trim()).filter(Boolean),out=[];let para=[],bullets=[];
 const fp=()=>{if(para.length){out.push(`<p>${esc(para.join(' '))}</p>`);para=[];}};const fb=()=>{if(bullets.length){out.push(`<ul>${bullets.map(x=>`<li>${esc(x)}</li>`).join('')}</ul>`);bullets=[];}};
 for(const line of lines){if(/^[-•▪◦*]\s+/.test(line)){fp();bullets.push(line.replace(/^[-•▪◦*]\s+/,''));continue;}if(/^\d+[.)]\s+/.test(line)){fp();bullets.push(line.replace(/^\d+[.)]\s+/,''));continue;}fb();para.push(line);}fp();fb();el.innerHTML=out.join('');el.dataset.v102Formatted='1';});
}
function start(){mountSubjectHub();wireClicks();formatExplanations();}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',start);else start();
new MutationObserver(()=>{mountSubjectHub();formatExplanations();}).observe(document.documentElement,{childList:true,subtree:true});
})();
</script>'''
    s = s.replace('</body>', js + '\n</body>', 1)

p.write_text(s, encoding='utf-8')
print('V10.2 UI layer restored')
