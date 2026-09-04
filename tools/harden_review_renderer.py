from pathlib import Path
import json
import re

DATA_PREFIX = 'window.SUBJECT_QBANK_DATA='

REPLACEMENTS = [
    (r'HCO\s*3\s*■', 'HCO₃⁻'), (r'HCO■■', 'HCO₃⁻'), (r'NH4\s*■', 'NH₄⁺'),
    (r'Fe³■', 'Fe³⁺'), (r'Fe²■', 'Fe²⁺'), (r'Ca²■', 'Ca²⁺'), (r'Mg²■', 'Mg²⁺'),
    (r'H■CO■', 'H₂CO₃'), (r'PCO■', 'PCO₂'), (r'PO■', 'PO₂'), (r'FEV■', 'FEV₁'),
    (r'VO■', 'VO₂'), (r'DO■', 'DO₂'), (r'CO■', 'CO₂'), (r'O■', 'O₂'),
    (r'Na\s*■', 'Na⁺'), (r'K\s*■', 'K⁺'), (r'Cl\s*■', 'Cl⁻'), (r'H\s*■', 'H⁺'),
    (r'voltage■gated', 'voltage-gated'), (r'\[Na⁺\]inside■', '[Na⁺]inside'),
    (r'■-Actinin', 'α-Actinin'), (r'H2PO4■', 'H₂PO₄⁻'), (r'PO2■■', 'PO₂'),
    (r'PCO2■■', 'PCO₂'), (r'I■', 'I⁻'), (r'Pseudostrati■ed', 'Pseudostratified'),
    (r'fine-tune sound vibrations■■', 'fine-tune sound vibrations.'),
]


def clean_physiology_explanation(text):
    x = str(text or '')
    for pattern, replacement in REPLACEMENTS:
        flags = re.I if pattern in (r'voltage■gated', r'Pseudostrati■ed') else 0
        x = re.sub(pattern, replacement, x, flags=flags)
    x = x.replace('Table rendering failed', '').strip()
    x = re.sub(r'\s+([,.;:])', r'\1', x)
    x = re.sub(r'[ \t]{2,}', ' ', x).strip()
    return x


def patch_html(s):
    # Do not infer paragraph boundaries from ordinary prose. Explicit source
    # bullets are only list material when there is a real bullet run.
    marker = '  function splitSourceParagraphs(text){'
    if marker not in s:
        return s
    start = s.index(marker)
    end = s.index('\n  function parseOptionBlocks', start)
    new_split = r'''  function splitSourceParagraphs(text){
    const raw=String(text||'').replace(/\r/g,'').trim();
    if(!raw)return[];
    const lines=raw.split('\n'),chunks=[];
    const heading=/^(Algorithm|Investigations|Significance|Mechanism|Key point|Recognition|Cause|Regulation|Identification Tips|Other options|Correct Option|Simple carbohydrates|Polysaccharides|Locations of Various)\s*:?[ \t]*$/i;
    if(lines.length>1){
      let cur=[],bullets=false;
      const flush=()=>{if(cur.length)chunks.push(cur.join(' ').replace(/\s+/g,' ').trim());cur=[];bullets=false;};
      for(const line of lines){
        const t=line.trim(); if(!t){flush();continue;}
        if(heading.test(t)){flush();chunks.push(t);continue;}
        if(/^•\s*/.test(t)||/^[-–—]\s+/.test(t)){flush();cur=[t.replace(/^[-–—]\s+/,'• ')];bullets=true;continue;}
        cur.push(t);
      }
      flush(); return chunks.filter(Boolean);
    }
    const bulletCount=(raw.match(/•/g)||[]).length;
    if(bulletCount>=2){
      const parts=raw.split(/•/),intro=parts.shift().trim();
      if(intro)chunks.push(intro);
      for(const p of parts){const t=p.trim();if(t)chunks.push('• '+t);}
      return chunks.filter(Boolean);
    }
    return [raw.replace(/^•\s*/,'').trim()].filter(Boolean);
  }
'''
    s=s[:start]+new_split+s[end:]

    # Only build a table when the source contains recognisable row labels. No
    # values are invented; the flattened source is preserved verbatim.
    anchor='  function renderSourceTable(table){'
    if anchor in s and 'function parseFlattenedTable(text)' not in s:
      idx=s.index(anchor)
      parser=r'''  function parseFlattenedTable(text){
    const raw=String(text||'').replace(/\r/g,'').trim(); if(!raw)return null;
    const labels=['Definition','Mechanism','Function','Functions','Location','Structure','Stimulus','Response','Pathway','Purpose','Example','Examples','Type','Feature','Features','Site','Effect','Effects','Receptor','Components','Composition','Distribution','Action','Characteristics','Cause','Causes','Symptoms','Duration','Role','Production','Secretion','Cell Type','Hormone','Condition','Process','Outcome','Speed','Direction','Conduction','Myelination','Inhibition','Excitation','Binding','Activation','Signaling','Measurement','Details','Pressure','Clinical Significance','Clinical Findings','Primary mechanism','Site of action','Cell Entry','Receptor Location','Receptor Family','Signaling Mechanism','Intracellular Activity','Nature','Embryological Origin','Cellular Composition'];
    const rx=new RegExp('\\b('+labels.sort((a,b)=>b.length-a.length).map(x=>x.replace(/[.*+?^${}()|[\\]\\]/g,'\\\\$&')).join('|')+')\\b','gi');
    const ms=[...raw.matchAll(rx)]; if(ms.length<2||/•/.test(raw))return null;
    const rows=[]; for(let i=0;i<ms.length;i++){const a=ms[i].index+ms[i][0].length,b=i+1<ms.length?ms[i+1].index:raw.length,v=raw.slice(a,b).trim();if(v)rows.push([ms[i][1],v]);}
    if(rows.length<2)return null; return {heads:['Source label','Source value'],rows,flattened:true};
  }

'''
      s=s[:idx]+parser+s[idx:]
    s=s.replace('const table=parseSourceTable(mainText);','const table=parseSourceTable(mainText) || parseFlattenedTable(mainText);',1)
    s=s.replace("let normalized=String(text).replace(/\\r/g,'').trim();","let normalized=String(text).replace(/\\r/g,'').replace(/Table rendering failed/g,'').trim();",1)
    # Submit Test must dismiss the overlay before changing routes.
    s=s.replace('onclick="window.QB.submitExam(false)"','onclick="window.QB.closeQuestionNavigator();window.QB.submitExam(false)"',1)
    return s


def clean_subject_file(path, html=False):
    p=Path(path); s=p.read_text(encoding='utf-8')
    start=s.index(DATA_PREFIX)+len(DATA_PREFIX); end=s.find('</script>',start)
    if end<0:end=len(s)
    data=json.loads(s[start:end].strip().rstrip(';'))
    physiology=next((x for x in data.get('subjects',[]) if x.get('subject')=='Physiology'),None)
    if not physiology: raise SystemExit(f'{path}: Physiology dataset not found')
    changed=0
    for q in physiology.get('questions',[]):
        old=q.get('explanation') or ''; new=clean_physiology_explanation(old)
        if new!=old:q['explanation']=new;changed+=1
        for key in ('question','correctAnswerText'):
            old=q.get(key) or ''; new=clean_physiology_explanation(old)
            if new!=old:q[key]=new
        for o in q.get('options',[]):
            old=o.get('text') or ''; new=clean_physiology_explanation(old)
            if new!=old:o['text']=new
    encoded=json.dumps(data,ensure_ascii=False,separators=(',',':'))
    s=s[:start]+encoded+';\n\n'+s[end:]
    if html:s=patch_html(s)
    p.write_text(s,encoding='utf-8')
    print(f'{path}: cleaned {changed} Physiology explanations')


if __name__=='__main__':
    clean_subject_file('app/src/main/assets/index.html',html=True)
    clean_subject_file('app/src/main/assets/subjects_qbank_data.js',html=False)
