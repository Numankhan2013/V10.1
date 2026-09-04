from pathlib import Path
import json,re
DATA_PREFIX='window.SUBJECT_QBANK_DATA='
REPLACEMENTS=[
 (r'HCO\s*3\s*■','HCO₃⁻'),(r'HCO■■','HCO₃⁻'),(r'NH4\s*■','NH₄⁺'),(r'Fe³■','Fe³⁺'),(r'Fe²■','Fe²⁺'),(r'Ca²■','Ca²⁺'),(r'Mg²■','Mg²⁺'),(r'H■CO■','H₂CO₃'),(r'PCO■','PCO₂'),(r'PO■','PO₂'),(r'FEV■','FEV₁'),(r'VO■','VO₂'),(r'DO■','DO₂'),(r'CO■','CO₂'),(r'O■','O₂'),(r'Na\s*■','Na⁺'),(r'K\s*■','K⁺'),(r'Cl\s*■','Cl⁻'),(r'H\s*■','H⁺'),(r'voltage■gated','voltage-gated'),(r'\[Na⁺\]inside■','[Na⁺]inside'),(r'■-Actinin','α-Actinin'),(r'H2PO4■','H₂PO₄⁻'),(r'PO2■■','PO₂'),(r'PCO2■■','PCO₂'),(r'I■','I⁻'),(r'Pseudostrati■ed','Pseudostratified'),(r'fine-tune sound vibrations■■','fine-tune sound vibrations.'),
 (r'Ionotrop\s*ic\s+recep\s*tors','Ionotropic receptors'),(r'Metabot\s*ropic\s+receptor\s*s','Metabotropic receptors'),(r'Postsyn\s*aptic','Postsynaptic'),(r'Presyn\s*aptic','Presynaptic'),(r'Dis\s*trib\s*uti\s*on','Distribution'),(r'Neurotransmi\s*tt?er','Neurotransmitter'),(r'Func\s*tion','Function'),(r'char\s*acteris\s*tics','Characteristics'),(r'Pathophysiol\s*ogy','Pathophysiology'),(r'Physiolog\s*y','Physiology'),
]

def clean(x):
 x=str(x or '')
 for a,b in REPLACEMENTS:x=re.sub(a,b,x,flags=re.I)
 x=x.replace('Table rendering failed','').strip(); x=re.sub(r'\s+([,.;:])',r'\1',x); return x

def patch_html(s):
    pf=s.find('  function parseFlattenedTable(text){')
    if pf>=0:
        pe=s.find('  function renderSourceTable(table){',pf)
        if pe<0: raise ValueError('renderSourceTable marker missing')
        s=s[:pf]+s[pe:]

    a=s.index('  function splitSourceParagraphs(text){'); b=s.index('\n  function parseOptionBlocks',a)
    s=s[:a]+r'''  function splitSourceParagraphs(text){
    const raw=String(text||'').replace(/\r/g,'').trim(); if(!raw)return[];
    const lines=raw.split('\n'),out=[]; let cur='';
    const headings=/^(Algorithm|Key Points|Mechanism|Clinical|Jendrassik Maneuver|Alpha-Gamma Coactivation|Afferent Limb|Integration Center|Efferent Limb|Effector|Peripheral Signals|Leptin and Obesity|Role of Orexin|Center-Surround Model|Incorrect Options|Other options|Difference|Features|Characteristics|Components|Types|Function|Pathway|Note|Important)\s*:?$/i;
    const flush=()=>{if(cur.trim())out.push(cur.trim());cur='';};
    for(const rawLine of lines){const line=rawLine.trim();if(!line){flush();continue;}const bullet=/^(?:•|[-–—])\s*/.test(line);if(bullet){flush();out.push('• '+line.replace(/^(?:•|[-–—])\s*/,''));continue;}if(headings.test(line)){flush();out.push(line);continue;}cur=cur?(cur+' '+line):line;}
    flush();
    if(out.length===1){const n=(out[0].match(/•/g)||[]).length;if(n>=2){const parts=out[0].split(/•/),first=parts.shift().trim(),r=[];if(first)r.push(first);for(const p of parts){if(p.trim())r.push('• '+p.trim());}return r;}}
    return out.filter(Boolean);
  }
'''+s[b:]

    a=s.index('  function renderExplanationText(text,question){'); b=s.index('\n  function practiceHistory',a)
    renderer=r'''  function renderExplanationText(text,question){
    if(!text)return'';
    try{
      let normalized=String(text).replace(/\r/g,'').replace(/Table rendering failed/g,'').trim();
      normalized=normalized.replace(/^\s*(?:Explanation\s*:\s*)/i,'').trim();
      const blocks=splitSourceParagraphs(normalized), html=[]; let ref=[];
      const tableStart=/^(?:Type\s+(?:Subtype|Channel|Location|of)|Feature\s+(?:Myasthenia|Stretch|Motor|Somatosensory|Primary)|Aspect\s+(?:Protein|Static|Acute|T4|Details)|Phase\s+(?:Description|Membrane)|Condition\s+Description|Category\s+Type|Parameter\s+Description|Classification\s+Function|Pathway\s+Aspect|Type\s+Receptor\s+subtype)\b/i;
      const flushRef=()=>{if(!ref.length)return;const txt=ref.join(' ').replace(/\s+/g,' ').trim();if(txt)html.push(`<details class="source-reference-fold"><summary>Reference material</summary><div class="source-reference-text">${richText(txt)}</div></details>`);ref=[];};
      for(const p of blocks){
        if(tableStart.test(p)){flushRef();ref.push(p);continue;}
        if(ref.length){ref.push(p);continue;}
        if(/^•\s*/.test(p)) html.push(`<div class="explain-bullet"><span class="bullet-dot">•</span><div>${richText(p.replace(/^•\s*/,''))}</div></div>`);
        else if(/^(Algorithm|Key Points|Mechanism|Clinical|Jendrassik Maneuver|Alpha-Gamma Coactivation|Afferent Limb|Integration Center|Efferent Limb|Effector|Peripheral Signals|Leptin and Obesity|Role of Orexin|Center-Surround Model|Incorrect Options|Other options|Difference|Features|Characteristics|Components|Types|Function|Pathway|Note|Important)\s*:?(?:\s*)$/i.test(p)) html.push(`<div class="explain-section-title">${richText(p.replace(/:$/,''))}</div>`);
        else if(/^(?:Option\s+[A-E]|[A-E]\))[^.]{0,100}(?:ruled out|incorrect|wrong|not|does not|don't|is not)/i.test(p)) html.push(`<div class="explain-option-note">${richText(p)}</div>`);
        else html.push(`<p class="explain-paragraph">${richText(p)}</p>`);
      }
      flushRef(); return html.join('');
    }catch(e){console.error('Explanation renderer fallback',e);return `<p class="explain-paragraph">${richText(String(text||''))}</p>`;}
  }
'''
    s=s[:a]+renderer+s[b:]
    s=s.replace('${formatExplanation(q.explanation)}','${renderExplanationText(q.explanation,q)}')
    s=s.replace('onclick="window.QB.submitExam(false)">Submit Test','onclick="window.QB.closeQuestionNavigator();window.QB.submitExam(false)">Submit Test')
    s=s.replace("function submitExam(auto=false){const s=state.activeSession;if(!s||s.mode!=='exam')return;","function submitExam(auto=false){const s=state.activeSession;if(!s||s.mode!=='exam')return;closeQuestionNavigator();",1)
    # Review must never die because a single explanation or stale question ID is malformed.
    old="const q=BY_ID[s.questionIds[s.index]], selected=s.answers[q.id]||null, corr=Number(selected)===Number(q.correctOption);"
    new="const q=BY_ID[s.questionIds[s.index]]; if(!q) return testsPage(); const selected=s.answers[q.id]||null, corr=Number(selected)===Number(q.correctOption);"
    s=s.replace(old,new,1)
    css='''.explain-option-note{margin:10px 0;padding:11px 13px;border-left:3px solid #c9cce2;background:#f8f8fc;border-radius:10px;font-size:15px;line-height:1.62;color:#414352}.source-reference-fold{margin:14px 0;border:1px solid #e1e3ec;border-radius:14px;background:#fafbfe;overflow:hidden}.source-reference-fold summary{padding:12px 14px;cursor:pointer;font-size:12px;font-weight:850;color:#4a4d67}.source-reference-text{padding:0 14px 14px;font-size:15px;line-height:1.68;color:#454757}'''
    if '.explain-option-note{' not in s:
        pos=s.find('</style>'); s=s[:pos]+css+s[pos:]
    return s

def clean_file(path,html=False):
 p=Path(path);s=p.read_text(encoding='utf8');st=s.index(DATA_PREFIX)+len(DATA_PREFIX);en=s.find('</script>',st);raw=s[st:en].strip().rstrip(';');data=json.loads(raw)
 phy=next(x for x in data['subjects'] if x['subject']=='Physiology');ana=next(x for x in data['subjects'] if x['subject']=='Anatomy')
 for q in phy['questions']:
  for k in ('explanation','question','correctAnswerText'):q[k]=clean(q.get(k))
  for o in q.get('options',[]):o['text']=clean(o.get('text'))
 for q in ana['questions']:
  x=q.get('explanation') or ''
  for a,b in [(r'Corneal\s+V■','Corneal V1'),(r'Jaw Jerk V■','Jaw Jerk V3'),(r'sensory V■\s*\(Mandibular branch','sensory V3 (Mandibular branch'),(r'Lacrimation V■','Lacrimation V1'),(r'90■clockwise','90° clockwise'),(r'70■','70°'),(r'C5 to■■ T1','C5 to T1')]:x=re.sub(a,b,x)
  q['explanation']=x
 enc=json.dumps(data,ensure_ascii=False,separators=(',',':'));s=s[:st]+enc+';\n\n'+s[en:]
 if html:s=patch_html(s)
 p.write_text(s,encoding='utf8');print('hardened',path)

if __name__=='__main__':
 clean_file('app/src/main/assets/index.html',True)
 clean_file('app/src/main/assets/subjects_qbank_data.js',False)
