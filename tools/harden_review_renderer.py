from pathlib import Path
import json,re
DATA_PREFIX='window.SUBJECT_QBANK_DATA='
REPLACEMENTS=[
 (r'HCO\s*3\s*■','HCO₃⁻'),(r'HCO■■','HCO₃⁻'),(r'NH4\s*■','NH₄⁺'),(r'Fe³■','Fe³⁺'),(r'Fe²■','Fe²⁺'),(r'Ca²■','Ca²⁺'),(r'Mg²■','Mg²⁺'),(r'H■CO■','H₂CO₃'),(r'PCO■','PCO₂'),(r'PO■','PO₂'),(r'FEV■','FEV₁'),(r'VO■','VO₂'),(r'DO■','DO₂'),(r'CO■','CO₂'),(r'O■','O₂'),(r'Na\s*■','Na⁺'),(r'K\s*■','K⁺'),(r'Cl\s*■','Cl⁻'),(r'H\s*■','H⁺'),(r'voltage■gated','voltage-gated'),(r'\[Na⁺\]inside■','[Na⁺]inside'),(r'■-Actinin','α-Actinin'),(r'H2PO4■','H₂PO₄⁻'),(r'PO2■■','PO₂'),(r'PCO2■■','PCO₂'),(r'I■','I⁻'),(r'Pseudostrati■ed','Pseudostratified'),(r'fine-tune sound vibrations■■','fine-tune sound vibrations.'),]

def clean(x):
 x=str(x or '')
 for a,b in REPLACEMENTS:x=re.sub(a,b,x,flags=(re.I if 'voltage' in a or 'Pseudostrati' in a else 0))
 x=x.replace('Table rendering failed','').strip(); x=re.sub(r'\s+([,.;:])',r'\1',x); x=re.sub(r'[ \t]{2,}',' ',x).strip(); return x

def patch_html(s):
    # Remove the previous flattened-table heuristic entirely. It created misleading
    # Source label / Source value cards from text whose column boundaries were lost.
    pf=s.find('  function parseFlattenedTable(text){')
    if pf>=0:
        pe=s.find('  function renderSourceTable(table){',pf)
        if pe<0: raise ValueError('renderSourceTable marker missing')
        s=s[:pf]+s[pe:]

    marker='  function splitSourceParagraphs(text){'
    if marker not in s:
        raise ValueError('splitSourceParagraphs marker missing')
    a=s.index(marker); b=s.index('\n  function parseOptionBlocks',a)
    split=r'''  function splitSourceParagraphs(text){
    const raw=String(text||'').replace(/\r/g,'').trim(); if(!raw)return[];
    const lines=raw.split('\n'),chunks=[];
    const heading=/^(Algorithm|Investigations|Significance|Mechanism|Key point|Recognition|Cause|Regulation|Identification Tips|Other options|Correct Option|Simple carbohydrates|Polysaccharides|Locations of Various)\s*:?[ \t]*$/i;
    if(lines.length>1){let cur=[];const flush=()=>{if(cur.length)chunks.push(cur.join(' ').replace(/\s+/g,' ').trim());cur=[];};for(const line of lines){const t=line.trim();if(!t){flush();continue;}if(heading.test(t)){flush();chunks.push(t);continue;}if(/^•\s*/.test(t)||/^[-–—]\s+/.test(t)){flush();cur=[t.replace(/^[-–—]\s+/,'• ')];continue;}cur.push(t);}flush();return chunks.filter(Boolean);}
    const n=(raw.match(/•/g)||[]).length;if(n>=2){const parts=raw.split(/•/),intro=parts.shift().trim();if(intro)chunks.push(intro);for(const p of parts){const t=p.trim();if(t)chunks.push('• '+t);}return chunks.filter(Boolean);}
    return [raw.replace(/^•\s*/,'').trim()].filter(Boolean);
  }
'''
    s=s[:a]+split+s[b:]

    marker='  function renderExplanationText(text,question){'
    i=s.index(marker)
    parser=r'''  function parseStructuredOptionExplanation(text,question){
    const raw=String(text||'').replace(/\r/g,'').trim();
    const split=raw.search(/\bIncorrect\s+Options?\s*:/i); if(split<0)return null;
    const correctPart=raw.slice(0,split).trim();
    const incorrectPart=raw.slice(split).replace(/^\bIncorrect\s+Options?\s*:\s*/i,'').trim();
    let correctLetter='',correctBody=correctPart;
    const cm=correctPart.match(/^(?:Correct\s+(?:Answer|Option)?|Answer)\s*[:\-]?\s*([A-E])\s*(?:\)|[-:])?\s*(.*)$/is);
    if(cm){correctLetter=cm[1].toUpperCase();correctBody=cm[2].trim();}
    const marker=/(?:\bOption\s+([A-E])\s*[-:]|\(\s*Option\s+([A-E])\s*\))/ig,ms=[...incorrectPart.matchAll(marker)];
    if(!ms.length)return null;
    const items=[];
    for(let i=0;i<ms.length;i++){const m=ms[i],letter=(m[1]||m[2]).toUpperCase(),end=i+1<ms.length?ms[i+1].index:incorrectPart.length;let body=incorrectPart.slice(m.index+m[0].length,end).trim();const opt=(question?.options||[]).find(o=>String(o.letter).toUpperCase()===letter);const title=opt?.text||`Option ${letter}`;items.push({letter,title,body});}
    return {correctLetter,correctBody,items};
  }

  function renderStructuredOptionExplanation(data,question){
    const correct=Number(question?.correctOption||0), correctLetter=data.correctLetter||(correct?String.fromCharCode(64+correct):'');
    const intro=data.correctBody?`<div class="explain-section-title">Why the correct answer is correct</div><p class="explain-paragraph">${richText(data.correctBody)}</p>`:'';
    const list=data.items.map(x=>`<article class="explain-option-item ${x.letter===correctLetter?'fits':''}"><div class="explain-option-head"><span class="explain-tag">Option ${x.letter}</span><span>${richText(x.title)}</span></div><div class="explain-option-reason">${x.letter===correctLetter?'Why it fits':'Why it doesn’t fit'}</div><div class="explain-option-body">${richText(x.body||'The supplied source does not provide a separate reason for this option.')}</div></article>`).join('');
    return `${intro}<div class="explain-section-title option-review-title">Why the other options don’t fit</div><div class="explain-option-list">${list}</div>`;
  }

'''
    s=s[:i]+parser+s[i:]

    a=s.index('  function renderExplanationText(text,question){'); b=s.index('\n  function practiceHistory',a)
    renderer=r'''  function renderExplanationText(text,question){
    if(!text)return'';
    let normalized=String(text).replace(/\r/g,'').replace(/Table rendering failed/g,'').trim();
    normalized=normalized.replace(/^\s*(?:Explanation\s*:\s*)/i,'').trim();
    const structured=parseStructuredOptionExplanation(normalized,question); if(structured)return renderStructuredOptionExplanation(structured,question);
    const blocks=[];
    const table=parseSourceTable(normalized);
    if(table){const lines=normalized.split('\n'),intro=lines.slice(0,table.startLine).join('\n').trim();if(intro)blocks.push(renderPlainExplanation(intro));blocks.push(renderSourceTable(table));const remainder=lines.slice(table.consumedLines).join('\n').trim();if(remainder)blocks.push(renderPlainExplanation(remainder));}
    else blocks.push(renderPlainExplanation(normalized));
    return blocks.filter(Boolean).join('');
  }
'''
    s=s[:a]+renderer+s[b:]
    s=s.replace('${formatExplanation(q.explanation)}','${renderExplanationText(q.explanation,q)}')
    s=s.replace('onclick="window.QB.submitExam(false)">Submit Test','onclick="window.QB.closeQuestionNavigator();window.QB.submitExam(false)">Submit Test')
    s=s.replace("function submitExam(auto=false){const s=state.activeSession;if(!s||s.mode!=='exam')return;","function submitExam(auto=false){const s=state.activeSession;if(!s||s.mode!=='exam')return;closeQuestionNavigator();",1)
    return s

def clean_file(path,html=False):
 p=Path(path);s=p.read_text(encoding='utf8');st=s.index(DATA_PREFIX)+len(DATA_PREFIX);en=s.find('</script>',st);raw=s[st:en].strip().rstrip(';');data=json.loads(raw);phy=next(x for x in data['subjects'] if x['subject']=='Physiology');changed=0
 for q in phy['questions']:
  old=q.get('explanation') or '';new=clean(old)
  if new!=old:q['explanation']=new;changed+=1
  for k in ('question','correctAnswerText'):
   old=q.get(k) or '';new=clean(old)
   if new!=old:q[k]=new
  for o in q.get('options',[]):
   old=o.get('text') or '';new=clean(old)
   if new!=old:o['text']=new
 enc=json.dumps(data,ensure_ascii=False,separators=(',',':'));s=s[:st]+enc+';\n\n'+s[en:]
 if html:s=patch_html(s)
 p.write_text(s,encoding='utf8');print(path,'changed',changed)

if __name__=='__main__':
 clean_file('app/src/main/assets/index.html',True)
 clean_file('app/src/main/assets/subjects_qbank_data.js',False)
