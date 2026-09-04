from pathlib import Path

p = Path('app/src/main/assets/index.html')
s = p.read_text(encoding='utf-8')
marker = '<!-- V104_EXPLANATION_RENDER -->'

if marker in s:
    print('Explanation renderer already present; leaving index.html unchanged')
    raise SystemExit(0)

css = r'''<style id="v104-explanation-css">
/* V10.4 explanation presentation: readable content, independent scroll, fixed actions. */
.explanation,.explanation-body,.feedback-body{box-sizing:border-box}
.qb-explanation-shell{margin-top:14px;border:1px solid var(--line);border-radius:16px;background:#fff;overflow:hidden;display:flex;flex-direction:column;min-height:0}
.qb-explanation-scroll{overflow:auto;max-height:min(48vh,430px);padding:15px 15px 18px;-webkit-overflow-scrolling:touch;overscroll-behavior:contain}
.qb-ex-answer{display:flex;align-items:flex-start;gap:10px;padding:12px 13px;margin:0 0 13px;border:1px solid #b9e2d1;border-radius:13px;background:#f1fbf6}
.qb-ex-answer-label{font-size:10px;font-weight:900;letter-spacing:.55px;text-transform:uppercase;color:var(--success);white-space:nowrap;padding-top:2px}
.qb-ex-answer-text{font-size:14px;line-height:1.45;font-weight:850;color:#202238}
.qb-ex-section{margin:0 0 15px}.qb-ex-section:last-child{margin-bottom:0}
.qb-ex-title{display:flex;align-items:center;gap:7px;margin:0 0 7px;font-size:12px;line-height:1.3;font-weight:900;color:var(--primary);letter-spacing:.15px}
.qb-ex-title:before{content:'';width:3px;height:15px;border-radius:3px;background:var(--primary);flex:0 0 auto}
.qb-ex-p{margin:0 0 8px;font-size:13px;line-height:1.62;color:#383b4a}
.qb-ex-p:last-child{margin-bottom:0}
.qb-ex-list{margin:4px 0 9px 20px;padding:0;color:#383b4a;font-size:13px;line-height:1.6}.qb-ex-list li{padding-left:3px;margin:4px 0}
.qb-ex-list li::marker{font-weight:800}
.qb-ex-label{font-weight:850;color:#272940}
.qb-ex-table-wrap{overflow-x:auto;margin:9px 0 13px;border:1px solid var(--line);border-radius:11px;-webkit-overflow-scrolling:touch}
.qb-ex-table{border-collapse:collapse;width:100%;min-width:440px;font-size:11.5px;line-height:1.45;color:#383b4a}
.qb-ex-table th,.qb-ex-table td{padding:8px 9px;text-align:left;vertical-align:top;border-bottom:1px solid var(--line)}
.qb-ex-table th{font-size:10.5px;font-weight:900;color:#292b40;background:#f7f7fa}
.qb-ex-table tr:last-child td{border-bottom:0}
.qb-ex-note{padding:10px 11px;margin:8px 0;border-left:3px solid var(--primary);border-radius:8px;background:#f7f7fb;font-size:12px;line-height:1.55;color:#3b3d4c}
/* Keep the question action area visible while explanation content scrolls. */
.question-card,.question-wrap,.practice-question,.exam-question{min-height:0}
.qb-explanation-actions{position:sticky;bottom:0;z-index:4;padding:10px 0 0;margin-top:0;background:linear-gradient(to bottom,rgba(255,255,255,0),#fff 22%)}
@media(max-width:640px){
  .qb-explanation-scroll{max-height:45vh;padding:13px 13px 16px}
  .qb-ex-p,.qb-ex-list{font-size:12.5px}
  .qb-ex-answer{padding:11px 12px}
  .qb-ex-table{min-width:410px}
}
</style>'''

js = r'''<script id="v104-explanation-render">
(function(){
  'use strict';
  const MARK='data-v104-explanation';
  const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const inline=v=>esc(v).replace(/\b(Correct Answer|Explanation|Key Point|Important|Note|Clinical correlation|Algorithm|Investigations|Diagnosis|Mechanism|Why|Other options)\b(?=\s*:)/gi,'<span class="qb-ex-label">$1</span>');

  function answerCard(line){
    const m=String(line).match(/^\s*Correct\s+Answer\s*:\s*(.+)$/i);
    if(!m)return '';
    return '<div class="qb-ex-answer"><div class="qb-ex-answer-label">Correct answer</div><div class="qb-ex-answer-text">'+inline(m[1])+'</div></div>';
  }

  function isHeading(line){
    const t=String(line).trim();
    if(!t)return false;
    if(/^Explanation\s*:?$/i.test(t))return true;
    if(/^(?:Key Point|Key Points|Important|Note|Clinical correlation|Algorithm|Investigations|Diagnosis|Mechanism|Why|Other options|Other option|Summary|Take[- ]?home message)\s*:??$/i.test(t))return true;
    return /^[A-Z][A-Za-z0-9 /&()'’+\-]{2,55}:$/.test(t) && !/[.!?]$/.test(t.slice(0,-1));
  }

  function isBullet(line){return /^(?:[-•▪◦*]|\d+[.)])\s+/.test(String(line).trim());}

  function splitTableRow(line){
    const t=String(line).trim();
    if(!t)return [];
    const cells=t.split(/\s{2,}/).map(x=>x.trim()).filter(Boolean);
    return cells.length>=2?cells:[];
  }

  function looksLikeTable(lines){
    if(lines.length<2)return false;
    const rows=lines.map(splitTableRow);
    return rows.filter(r=>r.length>=2).length>=Math.max(2,Math.ceil(lines.length*.6));
  }

  function renderTable(lines){
    const rows=lines.map(splitTableRow).filter(r=>r.length>=2);
    if(rows.length<2)return '';
    const width=Math.max.apply(null,rows.map(r=>r.length));
    const normalized=rows.map(r=>{while(r.length<width)r.push('');return r;});
    const head=normalized[0];
    let h='<div class="qb-ex-table-wrap"><table class="qb-ex-table"><thead><tr>'+head.map(c=>'<th>'+inline(c)+'</th>').join('')+'</tr></thead><tbody>';
    for(let i=1;i<normalized.length;i++)h+='<tr>'+normalized[i].map(c=>'<td>'+inline(c)+'</td>').join('')+'</tr>';
    return h+'</tbody></table></div>';
  }

  function rich(text){
    let raw=String(text??'').replace(/\r\n?/g,'\n').trim();
    if(!raw)return '';
    const lines=raw.split('\n');
    const out=[]; let para=[]; let bullets=[]; let ordered=false; let table=[];
    const flushPara=()=>{if(!para.length)return;const x=para.join(' ').replace(/\s+/g,' ').trim();if(x)out.push('<p class="qb-ex-p">'+inline(x)+'</p>');para=[];};
    const flushList=()=>{if(!bullets.length)return;out.push('<ul class="qb-ex-list">'+bullets.map(x=>'<li>'+inline(x)+'</li>').join('')+'</ul>');bullets=[];ordered=false;};
    const flushTable=()=>{if(!table.length)return;const t=renderTable(table);if(t)out.push(t);else table.forEach(x=>para.push(x));table=[];};
    const flushAll=()=>{flushTable();flushPara();flushList();};

    for(let i=0;i<lines.length;i++){
      const rawLine=lines[i], line=rawLine.trim();
      if(!line){flushAll();continue;}
      if(/^Correct\s+Answer\s*:/i.test(line)){flushAll();out.push(answerCard(line));continue;}
      if(isHeading(line)){flushAll();const title=line.replace(/:\s*$/,'').trim();if(!/^Explanation$/i.test(title))out.push('<div class="qb-ex-section"><div class="qb-ex-title">'+esc(title)+'</div>');else out.push('<div class="qb-ex-section">');continue;}
      const bullet=line.match(/^(?:[-•▪◦*]|\d+[.)])\s+(.*)$/);
      if(bullet){flushTable();flushPara();bullets.push(bullet[1]);continue;}
      if(table.length||splitTableRow(line).length>=2){
        const row=splitTableRow(line);
        if(row.length>=2){flushPara();flushList();table.push(line);continue;}
        if(table.length){flushTable();}
      }
      flushTable();flushList();para.push(line);
      // Close a section opened by a heading when the next heading arrives; DOM nesting is repaired below.
    }
    flushAll();
    let html=out.join('');
    // Heading sections are visual wrappers; close any remaining wrappers conservatively.
    html=html.replace(/(<div class="qb-ex-section">(?:(?!<div class="qb-ex-section").)*?)(?=<div class="qb-ex-section">|$)/gs,'$1</div>');
    return html;
  }

  function targetText(el){
    if(!el||el.closest('.qb-explanation-shell'))return '';
    const txt=el.textContent||'';
    if(!txt.trim())return '';
    if(!/(Correct\s+Answer|Explanation\s*:|\bExplanation\b)/i.test(txt))return '';
    return txt;
  }

  function formatOne(el){
    if(!el||el.getAttribute(MARK)==='1')return;
    const txt=targetText(el); if(!txt)return;
    const html=rich(txt); if(!html)return;
    const shell=document.createElement('div'); shell.className='qb-explanation-shell'; shell.setAttribute(MARK,'1');
    const scroll=document.createElement('div'); scroll.className='qb-explanation-scroll'; scroll.innerHTML=html;
    shell.appendChild(scroll);
    el.innerHTML=''; el.appendChild(shell); el.setAttribute(MARK,'1');
  }

  function scan(){
    const selectors=['.feedback-body','.explanation-body','.explanation','.feedback','.solution','.solution-body'];
    const seen=new Set();
    selectors.forEach(sel=>document.querySelectorAll(sel).forEach(el=>{if(!seen.has(el)){seen.add(el);formatOne(el);}}));
  }
  function start(){scan();let n=0;const mo=new MutationObserver(()=>{if(n++<120)scan();});mo.observe(document.documentElement,{childList:true,subtree:true});setTimeout(()=>mo.disconnect(),20000);}
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',start,{once:true});else start();
})();
</script>'''

s=s.replace('</head>',css+'\n</head>',1)
s=s.replace('</body>',js+'\n'+marker+'\n</body>',1)
p.write_text(s,encoding='utf-8')
print('V10.4 explanation renderer appended')