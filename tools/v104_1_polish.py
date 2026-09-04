from pathlib import Path

HTML=Path('app/src/main/assets/index.html')
s=HTML.read_text(encoding='utf-8')

css=r'''<style id="v104-1-polish">
.v104-command{margin:18px 0;padding:22px;border-radius:24px;background:linear-gradient(135deg,rgba(49,91,234,.10),rgba(109,77,245,.08) 55%,rgba(22,163,106,.07));border:1px solid rgba(49,91,234,.13);box-shadow:0 18px 45px rgba(25,39,68,.07)}
.v104-command-head{display:flex;align-items:center;justify-content:space-between;gap:14px}.v104-command h2{margin:4px 0;font-size:25px;letter-spacing:-.035em}.v104-command p{margin:5px 0 0;color:var(--v-muted)}
.v104-command-actions{display:flex;gap:9px;flex-wrap:wrap;margin-top:17px}.v104-chip{display:inline-flex;align-items:center;gap:7px;padding:7px 11px;border-radius:999px;background:rgba(255,255,255,.7);border:1px solid var(--v-border);font-size:12px;font-weight:800;color:var(--v-muted)}
.v104-statbar{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-top:14px}.v104-mini{padding:14px 15px;border-radius:16px;background:rgba(255,255,255,.62);border:1px solid rgba(25,39,68,.07)}.v104-mini b{font-size:21px;display:block;letter-spacing:-.03em}.v104-mini span{font-size:11px;color:var(--v-muted);font-weight:750}
.v104-press{transition:transform .16s ease,box-shadow .16s ease}.v104-press:active{transform:scale(.985)}
@media(max-width:680px){.v104-command-head{align-items:flex-start;flex-direction:column}.v104-statbar{grid-template-columns:1fr 1fr}.v104-mini:last-child{grid-column:1/-1}}
</style>'''

js=r'''<script id="v104-1-runtime">
(function(){'use strict';
function readState(){try{return window.QB&&window.QB.getState?window.QB.getState()||{}:JSON.parse(localStorage.getItem('qbank_state_v1')||'{}')}catch(e){return {}}}
function countAnswers(st){var n=0;try{Object.keys(st.answers||{}).forEach(function(k){if(st.answers[k])n++});}catch(e){}return n}
function testCount(st){return Array.isArray(st.tests)?st.tests.length:0}
function streak(st){var v=st.streak; if(typeof v==='number')return v; if(st.stats&&typeof st.stats.streak==='number')return st.stats.streak; return 0}
function lastBackup(){try{var x=JSON.parse(localStorage.getItem('qbank_backup_meta_v2')||'null');return x&&x.createdAt?new Date(x.createdAt):null}catch(e){return null}}
function due(st){var pref=localStorage.getItem('qbank_backup_schedule_v1')||'Off';var last=lastBackup();if(pref==='Off'||!last)return false;var days=pref==='Weekly'?7:3;return Date.now()-last.getTime()>=days*86400000}
function fmt(d){if(!d)return 'No backup yet';try{return d.toLocaleString()}catch(e){return String(d)}}
function goPractice(){try{if(window.QB&&window.QB.startPractice){window.QB.startPractice();return}}catch(e){}try{location.hash='#practice'}catch(e){}}
function dashboardPolish(){if(document.querySelector('.v104-command'))return;var page=document.querySelector('.page');if(!page)return;var head=page.querySelector('.page-head');if(!head)return;
 var st=readState(),tests=testCount(st),answers=countAnswers(st),sk=streak(st),lb=lastBackup();
 var box=document.createElement('section');box.className='v104-command v104-press';box.innerHTML='<div class="v104-command-head"><div><div class="v104-kicker">Your study cockpit</div><h2>What should I do next?</h2><p>Pick up where you left off and keep your momentum moving.</p></div><span class="v104-chip">NK QBank · V10.4</span></div><div class="v104-statbar"><div class="v104-mini"><b>'+answers+'</b><span>answered this session</span></div><div class="v104-mini"><b>'+tests+'</b><span>tests saved</span></div><div class="v104-mini"><b>'+sk+'</b><span>day streak</span></div></div><div class="v104-command-actions"><button class="primary-btn" id="v104-next-practice">Continue Practice</button><button class="ghost-btn" id="v104-open-backup">Protect My Data</button></div><div style="margin-top:12px;font-size:12px;color:var(--v-muted)">Backup status · '+(due(st)?'<b>Backup recommended</b>':'Last backup: '+fmt(lb))+'</div>';
 head.insertAdjacentElement('afterend',box);box.querySelector('#v104-next-practice').onclick=goPractice;box.querySelector('#v104-open-backup').onclick=function(){if(window.QB&&window.QB.openBackup)window.QB.openBackup()};
}
function backupMeta(){try{localStorage.setItem('qbank_backup_meta_v2',JSON.stringify({createdAt:new Date().toISOString(),version:2}))}catch(e){}}
var oldExport=window.QB&&window.QB.exportBackup;if(window.QB){window.QB.markBackupComplete=backupMeta}
var observer=new MutationObserver(function(){dashboardPolish()});observer.observe(document.documentElement,{childList:true,subtree:true});setTimeout(dashboardPolish,350);
})();
</script>'''

if 'id="v104-1-polish"' not in s:s=s.replace('</head>',css+'\n</head>',1)
if 'id="v104-1-runtime"' not in s:s=s.replace('</body>',js+'\n</body>',1)
HTML.write_text(s,encoding='utf-8')
print('V10.4.1 polish layer installed')
