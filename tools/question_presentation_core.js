  /* NK_QUESTION_PRESENTATION_V1_START
     Normalize extraction-shaped choices once, then render matching questions
     semantically across Practice, CBT, and Review without rewriting source data. */
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

  function nkQuestionStemMarkup(q){
    const presentation=nkQuestionPresentationFor(q),matching=nkQuestionMatchingSource(q,presentation),continuation=matching?null:nkQuestionContinuationSource(q,presentation),table=nkQuestionMatchingTable(matching||continuation,Boolean(continuation));
    const unavailable=presentation.valid?'':`<div class="nk-question-unavailable" role="status"><strong>Answer choices unavailable</strong><span>This source record is incomplete, so answering is disabled instead of recording an unreliable result.</span></div>`;
    if(!table)return `<span class="nk-question-prompt">${esc(String(q?.question||'').replace(/\*\*Type:\*\*\s*Match the Following/ig,'').trim())}</span>${unavailable}`;
    const headers=table.groups.map((_,index)=>`<th scope="col">${table.groups.length===1?'Statements':`List ${['I','II','III'][index]||index+1}`}</th>`).join('');
    const rows=table.rows.map(row=>`<tr>${row.map(cell=>`<td>${cell?`<b>${esc(cell.label)}</b><span>${esc(cell.value)}</span>`:'<span aria-hidden="true">—</span>'}</td>`).join('')}</tr>`).join('');
    return `<span class="nk-question-prompt">${esc(table.prompt)}</span><div class="nk-match-table-scroll"><table class="nk-match-table"><thead><tr>${headers}</tr></thead><tbody>${rows}</tbody></table></div>${unavailable}`;
  }

  nkNormalizeQuestionPresentationCorpus();
  /* NK_QUESTION_PRESENTATION_V1_END */
