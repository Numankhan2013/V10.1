  /* NK_QUESTION_PRESENTATION_V1_START
     Normalize extraction-shaped choices once, then render matching questions
     semantically across Practice, CBT, and Review without rewriting source data. */
  function nkNormalizeScientificDisplayText(text){
    // Repair only notation whose missing OCR glyph is unambiguous. Ambiguous
    // source loss (for example, whether ■-1,4 was alpha or beta) stays visible
    // for source-backed content review instead of being guessed here.
    return String(text??'')
      .replace(/((?:P|p|Pa)(?:CO|O)2)■+/g,'$1')
      .replace(/H\s*■\s*O/g,'H2O')
      .replace(/FADH■/g,'FADH2')
      .replace(/NADP■/g,'NADP+')
      .replace(/NAD■/g,'NAD+')
      .replace(/HCO\s*(?:3\s*)?■+/g,'HCO3−')
      .replace(/NH4\s*■/g,'NH4+')
      .replace(/CO■/g,'CO2')
      .replace(/O■/g,'O2')
      .replace(/\b(Ca|Mg|Fe|Cu|Zn|Mn)([²³])\s*■/g,(_,ion,magnitude)=>ion+(magnitude==='²'?'2':'3')+'+')
      .replace(/\b(Na|K)\s*■/g,'$1+')
      .replace(/\bCl\s*■/g,'Cl−')
      .replace(/\bH\s*■/g,'H+');
  }

  function nkScientificMarkup(text){
    let html=esc(nkNormalizeScientificDisplayText(text));
    const tokens=[];
    const stash=(kind,value)=>{const index=tokens.push(`<${kind} class="nk-sci-${kind}">${value}</${kind}>`)-1;return `\uE000${index}\uE001`;};

    // Explicit source notation always wins: x^4, 10^{-6}, SO4^2-, H_{2}O.
    html=html.replace(/([A-Za-z0-9)\]])\s*\^\s*\{\s*([+−-]?\d+[+−-]?|[+−-])\s*\}/g,(_,base,power)=>base+stash('sup',power.replace(/-/g,'−')));
    html=html.replace(/([A-Za-z0-9)\]])\s*\^\s*([+−-]?\d+[+−-]?|[+−-])/g,(_,base,power)=>base+stash('sup',power.replace(/-/g,'−')));
    html=html.replace(/([A-Za-z0-9)\]])\s*_\s*\{\s*([A-Za-z0-9,+−-]+)\s*\}/g,(_,base,index)=>base+stash('sub',index));

    // Ionic charge is a superscript. For monatomic ions the numeral is charge
    // magnitude (Ca2+), not an atom count; molecular ions are handled below.
    html=html.replace(/(^|[^A-Za-z0-9])(Ca|Mg|Fe|Cu|Zn|Mn)\s*([23])\s*([+−-])(?![A-Za-z0-9])/g,(_,lead,ion,magnitude,charge)=>lead+ion+stash('sup',magnitude+charge.replace(/-/g,'−')));
    html=html.replace(/(^|[^A-Za-z0-9])(H|Na|K|Cl)\s*([+−-])(?![A-Za-z0-9])/g,(_,lead,ion,charge)=>lead+ion+stash('sup',charge.replace(/-/g,'−')));

    // Common biochemical and physiological formulae are deliberately bounded.
    // This avoids turning ordinary identifiers and question numbers into maths.
    const formula=/(^|[^A-Za-z0-9])((?:(?:Pa|PA|pa|p|P)(?:CO2|O2))|C6H12O6|H2PO4|H2CO3|H2O2|HCO3|HPO4|FADH2|NADH2|NH4|SO4|PO4|CH2O|H2O|NH3|CO2|NO2|O2|N2)([+−-]?)(?![A-Za-z0-9])/g;
    html=html.replace(formula,(_,lead,value,charge)=>lead+value.replace(/\d+/g,digits=>stash('sub',digits))+(charge?stash('sup',charge.replace(/-/g,'−')):''));
    html=html.replace(/(^|[^A-Za-z0-9])HbA1c(?![A-Za-z0-9])/g,(_,lead)=>lead+'HbA'+stash('sub','1c'));
    html=html.replace(/([αβγ])([1-4])(?!\d)/g,(_,letter,index)=>letter+stash('sub',index));

    return html.replace(/\uE000(\d+)\uE001/g,(_,index)=>tokens[Number(index)]||'');
  }

  function nkQuestionOptionRuns(options){
    const runs=[];let current=[];
    (Array.isArray(options)?options:[]).forEach((option,index)=>{
      const letter=String(option?.letter||'').trim().toUpperCase();
      if(letter==='A'&&current.length){runs.push(current);current=[];}
      if(letter===String.fromCharCode(65+current.length))current.push({option,index});
      else {if(current.length)runs.push(current);current=letter==='A'?[{option,index}]:[];}
    });
    if(current.length)runs.push(current);
    return runs;
  }

  function nkQuestionChoiceScore(run,correctOption){
    if(!run?.length)return-1e6;
    const text=run.map(item=>String(item.option?.text||'')).join(' ');
    const complete=run.length>=4&&run.length<=5&&run.every((item,index)=>String(item.option?.letter||'').trim().toUpperCase()===String.fromCharCode(65+index));
    const mappings=(text.match(/\b(?:[A-Ea-e]|[1-9]|i{1,3}|iv|v)\s*[-:]\s*(?:[A-Ea-e]|[1-9]|i{1,3}|iv|v)\b/g)||[]).length;
    const explanation=/\b(?:incorrect options?|other options?|why it|explanation|fig(?:ure)?\s*:|the other options?)\b/i.test(text);
    return (complete?100:0)+(Number(correctOption)>=1&&Number(correctOption)<=run.length?20:0)+Math.min(20,mappings*2)-Math.max(0,run.length-5)*20-(explanation?18:0);
  }

  function nkQuestionPresentationFor(q){
    if(q?.__nkQuestionPresentation)return q.__nkQuestionPresentation;
    const original=Array.isArray(q?.options)?q.options.filter(Boolean):[];
    const runs=nkQuestionOptionRuns(original).filter(run=>run.length>=2);
    let chosen=runs.sort((a,b)=>nkQuestionChoiceScore(b,q?.correctOption)-nkQuestionChoiceScore(a,q?.correctOption)||a[0].index-b[0].index)[0]||[];
    if(chosen.length===5){
      const fifth=String(chosen[4]?.option?.text||'');
      if(Number(q?.correctOption)<=4&&/\b(?:incorrect options?|other options?|the other options?|explanation|fig(?:ure)?\s*:|is incorrect)\b/i.test(fifth))chosen=chosen.slice(0,4);
    }
    const chosenIndexes=new Set(chosen.map(item=>item.index));
    const options=chosen.map(item=>item.option);
    const supporting=original.filter((_,index)=>!chosenIndexes.has(index));
    const correct=Number(q?.correctOption);
    const valid=options.length>=2&&options.length<=5&&Number.isInteger(correct)&&correct>=1&&correct<=options.length&&options.every((option,index)=>String(option?.letter||'').trim().toUpperCase()===String.fromCharCode(65+index)&&String(option?.text||'').trim());
    const repaired=valid&&(options.length!==original.length||options.some((option,index)=>option!==original[index]));
    const presentation={options,supporting,valid,repaired,originalOptionCount:original.length};
    try{Object.defineProperty(q,'__nkQuestionPresentation',{value:presentation,configurable:true});}catch(_){q.__nkQuestionPresentation=presentation;}
    if(valid&&repaired)q.options=options;
    return presentation;
  }

  function nkQuestionCorpus(){
    const all=typeof nkAllBankQuestions==='function'?nkAllBankQuestions():(typeof SUBJECTS!=='undefined'?(SUBJECTS||[]).flatMap(record=>record?.questions||[]):[]);
    return [...new Set(all.filter(Boolean))];
  }

  function nkNormalizeQuestionPresentationCorpus(){
    const summary={questions:0,repaired:0,invalid:0};
    nkQuestionCorpus().forEach(q=>{const p=nkQuestionPresentationFor(q);summary.questions++;if(p.repaired)summary.repaired++;if(!p.valid)summary.invalid++;});
    return summary;
  }

  function nkQuestionMatchingSource(q,presentation){
    const question=String(q?.question||'');
    // Matching intent is cheap to recognize; structural evidence is the real gate.
    // Do not hard-code a vocabulary after "match" because valid source prompts vary
    // ("match the ion...", "match each...", "correct match ... Column A/B", etc.).
    if(!/\bmatch(?:ing)?\b/i.test(question)&&!/\*\*Type:\*\*\s*Match/i.test(question))return null;
    const support=(presentation?.supporting||[]).map(option=>`${String(option?.letter||'').trim()}. ${String(option?.text||'').trim()}`.trim()).filter(Boolean);
    return [question,...support].join(' ')
      .replace(/\*\*Type:\*\*\s*Match the Following/ig,' ')
      .replace(/\*\*Visual\s*\/\s*Image Reference:\*\*[\s\S]*$/i,' ')
      .replace(/\s+/g,' ').trim();
  }

  function nkQuestionContinuationSource(q,presentation){
    const question=String(q?.question||'');
    const support=(presentation?.supporting||[]).map(option=>`${String(option?.letter||'').trim()}. ${String(option?.text||'').trim()}`.trim()).filter(Boolean);
    if(!support.length||!/\bA[.)]\s+[\s\S]*\bB[.)]\s+/i.test(question)||!/^C[.)]\s+/i.test(support[0]))return null;
    return [question,...support].join(' ')
      .replace(/\*\*Visual\s*\/\s*Image Reference:\*\*[\s\S]*$/i,' ')
      .replace(/\s+/g,' ').trim();
  }

  function nkQuestionTrimRepeatedPrelude(value,prelude){
    const clean=String(value||'').replace(/\s+/g,' ').trim();
    const lead=String(prelude||'').replace(/\s+/g,' ').trim();
    if(!clean||!lead)return clean;
    const words=lead.split(' ');
    for(let index=0;index<words.length-1;index++){
      const suffix=words.slice(index).join(' ').trim();
      if(suffix.length<8)continue;
      if(clean.toLowerCase().endsWith((' '+suffix).toLowerCase()))return clean.slice(0,clean.length-suffix.length).trim();
    }
    return clean;
  }

  function nkQuestionBareMatchingTable(source){
    const marker=/(?:^|\s)(viii|vii|vi|iv|iii|ii|i|v|[a-h])(?=\s+\S)/g;
    const raw=[...source.matchAll(marker)];if(raw.length<6)return null;
    const rank={letter:['a','b','c','d','e','f','g','h'],roman:['i','ii','iii','iv','v','vi','vii','viii']};
    const seen={letter:new Set(),roman:new Set()},accepted=[];let repeatAt=-1;
    for(const hit of raw){
      const key=hit[1].toLowerCase(),family=key.length===1&&/[a-h]/.test(key)?'letter':'roman';
      if(seen[family].has(key)){
        if([...seen.letter].length>=3&&[...seen.roman].length>=3){repeatAt=hit.index||0;break;}
        continue;
      }
      const expected=rank[family][seen[family].size];
      if(key!==expected)continue;
      seen[family].add(key);accepted.push({hit,key,family});
    }
    if(seen.letter.size<3||seen.roman.size<3)return null;
    accepted.sort((a,b)=>(a.hit.index||0)-(b.hit.index||0));
    const first=accepted[0].hit.index||0,prelude=source.slice(0,first).trim();
    const groups={letter:[],roman:[]};
    accepted.forEach((entry,index)=>{
      const start=(entry.hit.index||0)+entry.hit[0].length;
      const end=index+1<accepted.length?(accepted[index+1].hit.index||source.length):(repeatAt>=0?repeatAt:source.length);
      let value=source.slice(start,end).trim();
      if(index===accepted.length-1)value=nkQuestionTrimRepeatedPrelude(value,prelude);
      if(value)groups[entry.family].push({label:entry.hit[1],value});
    });
    if(repeatAt>=0){
      const firstValues=[groups.letter[0]?.value,groups.roman[0]?.value].filter(value=>String(value||'').length>=4);
      for(const group of [groups.letter,groups.roman]){
        const last=group[group.length-1];if(!last)continue;
        for(const firstValue of firstValues){
          const at=last.value.indexOf(firstValue);if(at>0)last.value=last.value.slice(0,at).trim();
        }
      }
    }
    const list=[groups.letter,groups.roman].filter(group=>group.length>=3);
    if(list.length<2)return null;
    const rows=Array.from({length:Math.max(...list.map(group=>group.length))},(_,index)=>list.map(group=>group[index]||null));
    return {prompt:prelude||'Match the following.',groups:list,rows};
  }

  function nkQuestionMatchingTable(source,allowSingle=false){
    if(!source)return null;
    const marker=/(?:^|\s)([1-9]\d*|[A-Ha-h]|viii|vii|vi|iv|iii|ii|i|v)(?:[.)](?=\s|[A-Z])|(?=\s+[A-Ha-h][.)]))/g;
    const rawHits=[...source.matchAll(marker)];
    if(rawHits.length<4)return allowSingle?null:nkQuestionBareMatchingTable(source);
    const families={number:[],letter:[],roman:[]},seen={number:new Set(),letter:new Set(),roman:new Set()};
    const accepted=[];let firstAccepted=-1,repeatAt=-1;
    for(const hit of rawHits){
      const before=source.slice(Math.max(0,(hit.index||0)-16),hit.index||0);
      if(/\b(?:Column|List)\s*$/i.test(before))continue;
      const raw=hit[1],lower=raw.toLowerCase();
      const family=/^\d+$/.test(raw)?'number':/^(?:i|ii|iii|iv|v|vi|vii|viii)$/.test(lower)&&raw===lower?'roman':'letter';
      const key=family==='letter'?raw.toUpperCase():lower;
      if(seen[family].has(key)){
        const completeFamilies=Object.values(seen).filter(group=>group.size>=2).length;
        if(completeFamilies>=2){repeatAt=hit.index||0;break;}
        continue;
      }
      seen[family].add(key);accepted.push({hit,raw,family,key});if(firstAccepted<0)firstAccepted=hit.index||0;
    }
    const prelude=firstAccepted>=0?source.slice(0,firstAccepted).trim():'';
    accepted.forEach((entry,index)=>{
      const start=(entry.hit.index||0)+entry.hit[0].length;
      const end=index+1<accepted.length?(accepted[index+1].hit.index||source.length):(repeatAt>=0?repeatAt:source.length);
      let value=source.slice(start,end).trim().replace(/\*\*.*$/,'').trim().replace(/^["']|["']$/g,'');
      if(index===accepted.length-1)value=nkQuestionTrimRepeatedPrelude(value,prelude);
      families[entry.family].push({label:entry.raw,value});
    });
    const groups=Object.values(families).filter(items=>items.length>=2).sort((a,b)=>a[0].label.localeCompare(b[0].label,undefined,{numeric:true}));
    const informative=groups.filter(group=>group.filter(item=>String(item.value||'').trim()).length>=2);
    if(groups.length<(allowSingle?1:2)||!informative.length)return allowSingle?null:nkQuestionBareMatchingTable(source);
    const rows=Array.from({length:Math.max(...groups.map(group=>group.length))},(_,index)=>groups.map(group=>group[index]||null));
    let prompt=prelude;
    prompt=prompt.replace(/\b(?:Column|List)\s+[A-CI1-3](?:\s+(?:Column|List)\s+[A-CII1-3]){1,2}\s*$/i,'').trim();
    return {prompt:prompt||'Match the following.',groups,rows};
  }

  function nkQuestionOverrideGrid(prompt,columns,headers){
    const groups=(Array.isArray(columns)?columns:[]).filter(group=>Array.isArray(group)&&group.length);
    if(!groups.length)return null;
    const rows=Array.from({length:Math.max(...groups.map(group=>group.length))},(_,index)=>groups.map(group=>group[index]||null));
    return {prompt,groups,rows,headers};
  }

  function nkQuestionOverrideTable(prompt,left,right,headers){
    return nkQuestionOverrideGrid(prompt,[left,right],headers);
  }

  function nkQuestionMatchingOverride(q){
    const id=String(q?.id||''),question=String(q?.question||'').replace(/\s+/g,' ').trim();
    const matches=pattern=>pattern.test(question);
    const optionTexts=(Array.isArray(q?.options)?q.options:[]).map(option=>String(option?.text||'').trim());
    if(id==='physiology-9-22'&&Number(q?.sourcePage)===259&&optionTexts.join('|')==='1|2|3|4'&&matches(/type, direction and mediators of axonal transport/i)&&matches(/1\s+Anterograde\s+Cell body to axon terminal\s+Dynein/i))return nkQuestionOverrideGrid(
      'Which of the following statements accurately describes the type, direction and mediators of axonal transport?',
      [
        ['1','2','3','4'].map(value=>({label:'',value})),
        ['Anterograde','Anterograde','Retrograde','Retrograde'].map(value=>({label:'',value})),
        ['Cell body to axon terminal','Axon terminal to cell body','Axon terminal to cell body','Cell body to axon terminal'].map(value=>({label:'',value})),
        ['Dynein','Kinesin','Dynein','Kinesin'].map(value=>({label:'',value}))
      ],
      ['Statement','Type','Direction','Mediator']);
    if(id==='26-13'&&matches(/functional assessment tests/i))return nkQuestionOverrideTable(
      'Match the following vitamins with their respective functional assessment tests:',
      [{label:'1',value:'Vitamin B1 (Thiamine)'},{label:'2',value:'Vitamin B2 (Riboflavin)'},{label:'3',value:'Vitamin B6 (Pyridoxine)'},{label:'4',value:'Vitamin B12 (Cobalamin)'}],
      [{label:'a',value:'Measure urinary methylmalonic acid'},{label:'b',value:'Measure transketolase activity in red blood cells'},{label:'c',value:'Measure glutathione reductase activity in red blood cells'},{label:'d',value:'Measure activation of red blood cell transaminases with pyridoxal phosphate'}],
      ['Vitamins','Functional assessment tests']);
    if(id==='physiology-10-10'&&matches(/labeled parts of (?:the )?sarcomere/i))return nkQuestionOverrideTable(
      'Match the labeled parts of the sarcomere (A–E) with their correct names.',
      ['A','B','C','D','E'].map(label=>({label,value:'Source image label'})),
      [{label:'1',value:'Z-line'},{label:'2',value:'I-band'},{label:'3',value:'M-line'},{label:'4',value:'A-band'},{label:'5',value:'H-zone'}],
      ['Image labels','Candidate structures']);
    if(id==='physiology-36-7'&&matches(/actions of insulin/i))return nkQuestionOverrideTable(
      'Match the following actions of insulin with the correct category:',
      [{label:'1',value:'Cell growth'},{label:'2',value:'Reabsorption of K+, Na+, and phosphate from the kidney'},{label:'3',value:'Food intake'},{label:'4',value:'Entry of phosphate and magnesium into the cell'},{label:'5',value:'Body weight'},{label:'6',value:'Lipolysis'},{label:'7',value:'Potassium uptake into cells'}],
      [{label:'a',value:'Increased by insulin'},{label:'b',value:'Decreased by insulin'}],
      ['Insulin action','Category']);
    if(id==='anatomy-3-12'&&matches(/^Match the following:/i))return nkQuestionOverrideTable(
      'Match labels A–F in the source image with the correct basal-ganglia structures.',
      ['A','B','C','D','E','F'].map(label=>({label,value:'Source image label'})),
      [{label:'1',value:'Caudate nucleus'},{label:'2',value:'Globus pallidus'},{label:'3',value:'Putamen'},{label:'4',value:'Substantia nigra'},{label:'5',value:'Subthalamic nucleus'},{label:'6',value:'Thalamus'}],
      ['Image labels','Candidate structures']);
    if(id==='anatomy-14-3'&&matches(/locations in the middle ear/i))return nkQuestionOverrideTable(
      'Match the following structures with their respective locations in the middle ear:',
      [{label:'A',value:'Tympanic plexus'},{label:'B',value:'Head of malleus'},{label:'C',value:'Stapedius muscle'},{label:'D',value:'Tympanic membrane'}],
      [{label:'1',value:'Epitympanum'},{label:'2',value:'Lateral wall'},{label:'3',value:'Promontory of cochlea'},{label:'4',value:'Mesotympanum'}],
      ['Structures','Locations']);
    if(id==='anatomy-29-16'&&matches(/section of the heart.*match the marked/i))return nkQuestionOverrideTable(
      'Match the marked structures (A–D) in the source heart section with the candidate structures.',
      ['A','B','C','D'].map(label=>({label,value:'Source image label'})),
      [{label:'1',value:'Musculi pectinati'},{label:'2',value:'Anterior papillary muscle of left ventricle'},{label:'3',value:'Anterior papillary muscle of right ventricle'},{label:'4',value:'Anterior leaflet of mitral valve'},{label:'5',value:'Membranous part of ventricular septum'}],
      ['Image labels','Candidate structures']);
    if(id==='anatomy-29-33'&&matches(/auscultatory areas of the heart/i))return nkQuestionOverrideTable(
      'Match image markers 1–4 with the correct cardiac auscultatory areas.',
      ['1','2','3','4'].map(label=>({label,value:'Source image marker'})),
      [{label:'a',value:'Aortic area'},{label:'b',value:'Mitral area'},{label:'c',value:'Pulmonary area'},{label:'d',value:'Tricuspid area'}],
      ['Image markers','Candidate areas']);
    if(id==='anatomy-30-4'&&matches(/dermatomal distribution/i))return nkQuestionOverrideTable(
      'Match the following landmarks with their corresponding dermatomal distribution:',
      [{label:'A',value:'Thumb'},{label:'B',value:'Umbilicus'},{label:'C',value:'Knee'},{label:'D',value:'Dorsum of foot'}],
      [{label:'1',value:'L3'},{label:'2',value:'L5'},{label:'3',value:'C6'},{label:'4',value:'T10'}],
      ['Landmarks','Dermatomes']);
    return null;
  }

  function nkQuestionStemMarkup(q){
    const presentation=nkQuestionPresentationFor(q),matching=nkQuestionMatchingSource(q,presentation),continuation=matching?null:nkQuestionContinuationSource(q,presentation),table=nkQuestionMatchingTable(matching||continuation,Boolean(continuation))||nkQuestionMatchingOverride(q);
    const unavailable=presentation.valid?'':`<div class="nk-question-unavailable" role="status"><strong>Answer choices unavailable</strong><span>This source record is incomplete, so answering is disabled instead of recording an unreliable result.</span></div>`;
    if(!table)return `<span class="nk-question-prompt">${nkScientificMarkup(String(q?.question||'').replace(/\*\*Type:\*\*\s*Match the Following/ig,'').trim())}</span>${unavailable}`;
    const headers=table.groups.map((_,index)=>`<th scope="col">${nkScientificMarkup((table.headers||[])[index]||(table.groups.length===1?'Statements':`List ${['I','II','III'][index]||index+1}`))}</th>`).join('');
    const rows=table.rows.map(row=>`<tr>${row.map(cell=>`<td>${cell?`${String(cell.label||'').trim()?`<b>${nkScientificMarkup(cell.label)}</b>`:''}<span>${nkScientificMarkup(cell.value)}</span>`:'<span aria-hidden="true">—</span>'}</td>`).join('')}</tr>`).join('');
    return `<span class="nk-question-prompt">${nkScientificMarkup(table.prompt)}</span><div class="nk-match-table-scroll"><table class="nk-match-table"><thead><tr>${headers}</tr></thead><tbody>${rows}</tbody></table></div>${unavailable}`;
  }

  nkNormalizeQuestionPresentationCorpus();
  /* NK_QUESTION_PRESENTATION_V1_END */
