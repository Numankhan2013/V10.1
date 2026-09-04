from pathlib import Path
import json
import re

DATA_PREFIX = 'window.SUBJECT_QBANK_DATA='

REPLACEMENTS = [
    (r'HCO\s*3\s*■', 'HCO₃⁻'),
    (r'HCO■■', 'HCO₃⁻'),
    (r'NH4\s*■', 'NH₄⁺'),
    (r'Fe³■', 'Fe³⁺'),
    (r'Fe²■', 'Fe²⁺'),
    (r'Ca²■', 'Ca²⁺'),
    (r'Mg²■', 'Mg²⁺'),
    (r'H■CO■', 'H₂CO₃'),
    (r'PCO■', 'PCO₂'),
    (r'PO■', 'PO₂'),
    (r'FEV■', 'FEV₁'),
    (r'VO■', 'VO₂'),
    (r'DO■', 'DO₂'),
    (r'CO■', 'CO₂'),
    (r'O■', 'O₂'),
    (r'Na\s*■', 'Na⁺'),
    (r'K\s*■', 'K⁺'),
    (r'Cl\s*■', 'Cl⁻'),
    (r'H\s*■', 'H⁺'),
    (r'voltage■gated', 'voltage-gated'),
    (r'\[Na⁺\]inside■', '[Na⁺]inside'),
    (r'■-Actinin', 'α-Actinin'),
    (r'H2PO4■', 'H₂PO₄⁻'),
    (r'PO2■■', 'PO₂'),
    (r'PCO2■■', 'PCO₂'),
    (r'I■', 'I⁻'),
    (r'Pseudostrati■ed', 'Pseudostratified'),
    (r'fine-tune sound vibrations■■', 'fine-tune sound vibrations.'),
]


def clean_physiology_explanation(text):
    x = str(text or '')
    for pattern, replacement in REPLACEMENTS:
        flags = re.I if pattern in (r'voltage■gated', r'Pseudostrati■ed') else 0
        x = re.sub(pattern, replacement, x, flags=flags)

    # This was a renderer diagnostic accidentally persisted inside the data.
    x = x.replace('Table rendering failed', '').strip()

    # Only normalize whitespace/punctuation. Do not manufacture paragraph,
    # heading, bullet, or table boundaries in the data layer.
    x = re.sub(r'\s+([,.;:])', r'\1', x)
    x = re.sub(r'[ \t]{2,}', ' ', x).strip()
    return x


def patch_html(s):
    # The Physiology source is flattened to one line. Only explicit bullet
    # markers are promoted to list items when there is a genuine bullet run.
    # An isolated bullet remains ordinary prose so coherent paragraphs are not
    # turned into fake lists.
    start = s.index('  function splitSourceParagraphs(text){')
    end = s.index('\n  function parseOptionBlocks', start)
    new_split = r'''  function splitSourceParagraphs(text){
    const raw=String(text||'').replace(/\r/g,'').trim();
    if(!raw) return [];
    const lines=raw.split('\n');
    const chunks=[];
    const heading=/^(Algorithm|Investigations|Significance|Mechanism|Key point|Recognition|Cause|Regulation|Identification Tips|Other options|Correct Option|Simple carbohydrates|Polysaccharides|Locations of Various)\s*:?[ \t]*$/i;
    const emitLine=line=>{const t=line.trim();if(t)chunks.push(t);};
    const hasExplicitNewlines=lines.length>1;
    if(hasExplicitNewlines){
      let cur=[]; let inBullets=false;
      const flush=()=>{if(cur.length){chunks.push(cur.join(' ').replace(/\s+/g,' ').trim());cur=[];}inBullets=false;};
      for(const line of lines){
        const t=line.trim();
        if(!t){flush();continue;}
        if(heading.test(t)){flush();chunks.push(t);continue;}
        if(/^•\s*/.test(t) || /^[-–—]\s+/.test(t)){flush();cur=[t.replace(/^[-–—]\s+/,'• ')];inBullets=true;continue;}
        if(inBullets){cur.push(t);continue;}
        cur.push(t);
      }
      flush();
      return chunks.filter(Boolean);
    }
    const bulletCount=(raw.match(/•/g)||[]).length;
    if(bulletCount>=2){
      const parts=raw.split(/•/);
      const intro=parts.shift().trim();
      if(intro) emitLine(intro);
      for(const p of parts){ const t=p.trim(); if(t) chunks.push('• '+t); }
      return chunks.filter(Boolean);
    }
    return [raw.replace(/^•\s*/,'').trim()].filter(Boolean);
  }
'''
    s = s[:start] + new_split + s[end:]

    # Conservative fallback for flattened source tables. It never invents
    # missing cell values: it preserves each detected source row verbatim in a
    # dedicated value cell. The UI can therefore show a table-like structure
    # without pretending to know column boundaries that the flattened source no
    # longer contains.
    anchor = '  function renderSourceTable(table){'
    idx = s.index(anchor)
    parser = r'''  function parseFlattenedTable(text){
    const raw=String(text||'').replace(/\r/g,'').trim();
    if(!raw) return null;
    const starts=[
      'Feature','Aspect','Type','Phase','Condition','Category','Component','Parameter',
      'Classification','Site','Location','Pathway','Characteristics','Factors affecting OER',
      'Hb-O 2 dissociation curve shift','Part of Papez Circuit','Part of the Amygdala Circuit'
    ];
    const rowLabels=[
      'Definition','Mechanism','Function','Functions','Location','Structure','Stimulus','Response',
      'Pathway','Purpose','Example','Examples','Type','Feature','Features','Site','Effect','Effects',
      'Receptor','Components','Composition','Distribution','Action','Characteristics','Clinical Findings',
      'Cause','Causes','Symptoms','Duration','Role','Percentage','Production','Secretion','Cell Type',
      'Hormone','Condition','Process','Outcome','Speed','Direction','Conduction','Myelination',
      'Inhibition','Excitation','Binding','Activation','Signaling','Site of action','Primary mechanism',
      'Spatial effect','Onset and duration','Nature','Cell Entry','Receptor Location','Receptor Family',
      'Signaling Mechanism','Intracellular Activity','Measurement','Details','Pressure','Oxygen Delivery',
      'Oxygen Consumption','Clinical Significance','Embryological Origin','Cellular Composition',
      'Slow IPSP','Fast IPSP','Resting State','Depolarization','Overshoot','Repolarization','After-hyperpolarization','Return to Resting State',
      'Protanopia','Deuteranopia','Tritanopia','Salt','Sour','Sweet','Bitter','Umami','Cold Receptors','Warmth Receptors','Cold Pain Fibers','Heat Pain Fibers',
      'Aδ fiber','C fiber','Unmyelinated','Myelinated','Hyperkalemia','Hypokalemia','Static Lung Volumes & Capacities','Dynamic Lung Volumes & Capacities',
      'Restrictive diseases','Obstructive diseases','Variable Intrathoracic Obstruction','Variable Extrathoracic Obstruction',
      'Stagnant Hypoxia','Histotoxic hypoxia','Acute Oxygen Toxicity','Chronic Oxygen Toxicity',
      'Protein Hormones','Steroid Hormones','Peptide/Protein Hormones','Amine Hormones','Thyroid Hormones',
      'Primary Hyperaldosteronism','Secondary Hyperaldosteronism','T4','T3','D1','D2','D3','Acidophilic','Basophilic',
      'Adenohypophysis (Anterior Pituitary)','Neurohypophysis (Posterior Pituitary)','Type 1 Receptors','Type 2 Receptors',
      'Menstrual Phase','Follicular Phase (Pre-ovulatory)','Ovulatory Phase','Luteal Phase'
    ];
    const startRx=new RegExp('(?:^|\\.\\s+)('+starts.map(x=>x.replace(/[.*+?^${}()|[\\]\\\\]/g,'\\\\$&')).join('|')+')\\s+','i');
    const sm=startRx.exec(raw); if(!sm) return null;
    const start=sm.index+(raw[sm.index]==='.'?2:0);
    const tail=raw.slice(start).trim();
    if(/•/.test(tail)) return null;
    const rowRx=new RegExp('\\b('+rowLabels.sort((a,b)=>b.length-a.length).map(x=>x.replace(/[.*+?^${}()|[\\]\\\\]/g,'\\\\$&')).join('|')+')\\b','gi');
    const matches=[...tail.matchAll(rowRx)];
    const filtered=[];
    for(const m of matches){
      if(m.index<20) continue;
      const prevChar=m.index>0?tail[m.index-1]:'';
      if(prevChar && !/\\s/.test(prevChar)) continue;
      if(filtered.length && m.index-filtered[filtered.length-1].index<18) continue;
      filtered.push(m);
    }
    if(filtered.length<2) return null;
    const firstHeader=tail.slice(0,filtered[0].index).trim();
    if(!firstHeader || firstHeader.split(/\\s+/).length>18) return null;
    const rows=[];
    for(let i=0;i<filtered.length;i++){
      const m=filtered[i];
      const valueStart=m.index+m[0].length;
      const valueEnd=i+1<filtered.length?filtered[i+1].index:tail.length;
      const value=tail.slice(valueStart,valueEnd).trim();
      if(value) rows.push([m[1],value]);
    }
    if(rows.length<2) return null;
    return {heads:[sm[1],'Source values'],rows,startLine:0,consumedLines:1,flattened:true};
  }

'''
    s = s[:idx] + parser + s[idx:]

    s = s.replace('const table=parseSourceTable(mainText);', 'const table=parseSourceTable(mainText) || parseFlattenedTable(mainText);', 1)
    s = s.replace("let normalized=String(text).replace(/\\r/g,'').trim();", "let normalized=String(text).replace(/\\r/g,'').replace(/Table rendering failed/g,'').trim();", 1)

    # The navigator is a temporary overlay. Submission must remove it before
    # the results route is rendered; the close is also done inside submitExam
    # as a defensive invariant.
    s = s.replace(
        "const submit=exam?'<button type=\"button\" class=\"primary-btn qb-nav-submit\" onclick=\"window.QB.submitExam(false)\">Submit Test</button>':'';",
        "const submit=exam?'<button type=\"button\" class=\"primary-btn qb-nav-submit\" onclick=\"window.QB.closeQuestionNavigator();window.QB.submitExam(false)\">Submit Test</button>':'';",
        1,
    )
    s = s.replace(
        "function submitExam(auto=false){const s=state.activeSession;if(!s||s.mode!=='exam')return;",
        "function submitExam(auto=false){const s=state.activeSession;if(!s||s.mode!=='exam')return;closeQuestionNavigator();",
        1,
    )
    return s


def clean_subject_file(path):
    p = Path(path)
    s = p.read_text(encoding='utf-8')
    start = s.index(DATA_PREFIX) + len(DATA_PREFIX)
    end = s.find('</script>', start)
    if end < 0:
        end = len(s)
    raw = s[start:end].strip().rstrip(';')
    data = json.loads(raw)
    physiology = next((x for x in data.get('subjects', []) if x.get('subject') == 'Physiology'), None)
    if not physiology:
        raise SystemExit(f'{path}: Physiology dataset not found')

    changed = 0
    for q in physiology.get('questions', []):
        old = q.get('explanation') or ''
        new = clean_physiology_explanation(old)
        if new != old:
            q['explanation'] = new
            changed += 1
        for key in ('question', 'correctAnswerText'):
            old = q.get(key) or ''
            new = clean_physiology_explanation(old)
            if new != old:
                q[key] = new
        for option in q.get('options', []):
            old = option.get('text') or ''
            new = clean_physiology_explanation(old)
            if new != old:
                option['text'] = new

    encoded = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
    s = s[:start] + encoded + ';\n\n' + s[end:]
    s = patch_html(s)
    p.write_text(s, encoding='utf-8')
    print(f'{path}: cleaned {changed} Physiology explanations')


if __name__ == '__main__':
    clean_subject_file('app/src/main/assets/index.html')
    clean_subject_file('app/src/main/assets/subjects_qbank_data.js')
