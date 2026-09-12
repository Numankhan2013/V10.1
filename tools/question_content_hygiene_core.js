/* NK_QUESTION_CONTENT_HYGIENE_V1_START */
  const NK_MARROW_TEXT_KEYS = ['text','content','label','value','title','name','markdown','html','explanation','rationale','reason','description','question','stem','answer','optionText','whyCorrect','whyWrong'];
  const NK_MARROW_METADATA_KEYS = new Set(['id','key','type','kind','schema','version','page','pageNumber','source_page','sourcePage','source','attrs','metadata','meta']);

  function nkWholeJsonCandidate(value) {
    const text=String(value??'').trim();
    if(text.length<2)return false;
    return (text[0]==='{'&&text[text.length-1]==='}')||
      (text[0]==='['&&text[text.length-1]===']')||
      (text[0]==='"'&&text[text.length-1]==='"');
  }

  function nkStructuredText(value,depth=0) {
    if(value===null||value===undefined||depth>12)return '';
    if(typeof value==='string')return value;
    if(typeof value==='number'||typeof value==='boolean')return String(value);
    if(Array.isArray(value))return value.map(item=>nkStructuredText(item,depth+1)).filter(Boolean).join('\n');
    if(typeof value!=='object')return String(value);

    for(const key of NK_MARROW_TEXT_KEYS){
      if(Object.prototype.hasOwnProperty.call(value,key)){
        const nested=nkStructuredText(value[key],depth+1).trim();
        if(nested)return nested;
      }
    }

    return Object.entries(value)
      .filter(([key])=>!NK_MARROW_METADATA_KEYS.has(key))
      .map(([,nested])=>nkStructuredText(nested,depth+1).trim())
      .filter(Boolean)
      .join('\n');
  }

  function nkSanitizeMarrowText(value) {
    if(value===null||value===undefined)return '';
    if(typeof value!=='string')return nkStructuredText(value).trim();

    let current=value;
    let decoded=false;
    for(let pass=0;pass<2;pass++){
      if(!nkWholeJsonCandidate(current))break;
      try{
        const parsed=JSON.parse(current);
        current=typeof parsed==='string'?parsed:nkStructuredText(parsed);
        decoded=true;
      }catch(_error){
        break;
      }
    }
    return decoded?String(current).trim():value;
  }

  function nkSanitizeMarrowQuestion(question) {
    if(!question||typeof question!=='object')return question;
    const isMarrow=String(question.id||'').startsWith('marrow__');
    if(!isMarrow){
      question.question=nkCleanQuestionStem(question.question);
      return question;
    }

    question.question=nkCleanQuestionStem(nkSanitizeMarrowText(question.question));
    for(const key of ['explanation','rationale','solution','keyTakeaway','takeaway']){
      if(Object.prototype.hasOwnProperty.call(question,key))question[key]=nkSanitizeMarrowText(question[key]);
    }
    if(Array.isArray(question.options)){
      question.options.forEach(option=>{
        if(!option||typeof option!=='object'||Array.isArray(option))return;
        for(const key of ['text','explanation','rationale','whyWrong','whyCorrect']){
          if(Object.prototype.hasOwnProperty.call(option,key))option[key]=nkSanitizeMarrowText(option[key]);
        }
      });
    }
    return question;
  }

  function nkCleanQuestionStem(value) {
    return String(value||'')
      .replace(/\bPrep\s*ladder\s*X\s*Qbank\b(?:\s*[•·|–—-]\s*)?(?:Biochemistry|Physiology|Anatomy)?\s*Page\s+\d+\s+of\s+\d+\b/gi,' ')
      .replace(/\bPrep\s*ladder\s*X\s*Qbank\b(?:\s*[•·|–—-]\s*)?(?:Biochemistry|Physiology|Anatomy)?\b/gi,' ')
      .replace(/[ \t]+\n/g,'\n')
      .replace(/\n[ \t]+/g,'\n')
      .replace(/[ \t]{2,}/g,' ')
      .replace(/\n{3,}/g,'\n\n')
      .trim();
  }

  function nkTakeawayWords(value) {
    const stop=new Set(['this','that','with','from','into','than','then','which','what','when','where','have','has','were','been','being','their','there','about','answer','option','correct']);
    return String(value||'').toLowerCase().replace(/fibres?/g,'fiber').replace(/[^a-z0-9+]+/g,' ').split(/\s+/).filter(word=>word.length>=4&&!stop.has(word));
  }

  function nkTakeawayScore(value,tokens,answer) {
    const normalized=String(value||'').toLowerCase().replace(/fibres?/g,'fiber');
    const overlap=tokens.reduce((count,token)=>count+(normalized.includes(token)?1:0),0);
    const exact=answer.length>=5&&normalized.includes(answer.toLowerCase().replace(/fibres?/g,'fiber'))?3:0;
    return overlap+exact;
  }

  function nkFinishTakeaway(value) {
    const clean=String(value||'').replace(/\s+/g,' ').replace(/^[-–—:\s]+/,'').trim();
    if(!clean)return '';
    return /[.!?]$/.test(clean)?clean:`${clean}.`;
  }

  function nkTableTakeaway(lines,tokens,answer) {
    const rows=lines.map(line=>String(line||'').trim().split(/\s{2,}/).map(cell=>cell.trim()).filter(Boolean));
    let best=null;
    rows.forEach((cells,rowIndex)=>{
      if(cells.length<2)return;
      cells.forEach((cell,columnIndex)=>{
        const score=nkTakeawayScore(cell,tokens,answer)+(/\bby\b/i.test(cell)?2:0)+(cell.length>=30?.25:0);
        if(!best||score>best.score)best={cell,rowIndex,columnIndex,score};
      });
    });
    if(!best||best.score<2)return '';
    let fact=best.cell;
    for(let row=best.rowIndex+1;row<rows.length;row++){
      const continuation=rows[row][best.columnIndex]||'';
      if(!continuation||!fact||/[.!?]$/.test(fact)||!/^[a-z(]/.test(continuation))break;
      fact+=` ${continuation}`;
    }
    fact=fact.replace(/\s*\(Option\s+[A-E]\)\s*/ig,' ').replace(/\s+/g,' ').trim();
    const mechanism=fact.match(/\bby\s+(.+)$/i);
    if(mechanism&&mechanism[1].length>=12){
      return `${nkFinishTakeaway(answer)} This occurs by ${nkFinishTakeaway(mechanism[1]).replace(/^./,letter=>letter.toLowerCase())}`;
    }
    if(nkTakeawayScore(fact,tokens,answer)>=tokens.length&&fact.length>=30&&fact.toLowerCase().replace(/fibres?/g,'fiber').startsWith(tokens[0]))return nkFinishTakeaway(fact);
    return nkFinishTakeaway(answer);
  }

  function nkSourceTakeaway(q) {
    const reviewed=String(q?.keyTakeaway||q?.takeaway||'').replace(/\s+/g,' ').trim();
    if(reviewed.length>=24)return nkFinishTakeaway(reviewed);
    const option=Array.isArray(q?.options)?q.options[Number(q.correctOption)-1]:null;
    const answer=String(option?.text||'').replace(/\s+/g,' ').trim();
    let source=String(q?.explanation||'').replace(/\r/g,'\n');
    if(!answer||!source)return '';
    source=source
      .replace(/^\s*Correct\s+(?:Answer|answer|Option)\s*:?\s*[A-E]\)?[^\n]*\n?/i,'')
      .replace(/Explanation[ ]*:[ ]*/i,"")
      .replace(/[•▪◦]\s*/g,' ');
    const tokens=nkTakeawayWords(answer);
    if(!tokens.length)return '';
    const lines=source.split('\n');
    const tableTakeaway=nkTableTakeaway(lines,tokens,answer);
    if(tableTakeaway&&tableTakeaway!==nkFinishTakeaway(answer))return tableTakeaway;
    const prose=lines.filter(line=>!/^\s*\S.*\s{2,}\S/.test(line)).join(' ').replace(/\s+/g,' ').trim();
    const sentences=(prose.match(/[^.!?]+[.!?]+|[^.!?]+$/g)||[])
      .map(sentence=>sentence.replace(/^[-–—:\s]+/,'').replace(/\s*\(Option\s+[A-E]\)\s*/ig,' ').replace(/\s+/g,' ').trim())
      .filter(sentence=>sentence.length>=35&&sentence.length<=300&&/^[A-Z0-9]/.test(sentence));
    let best='',bestScore=0;
    sentences.forEach(sentence=>{
      const score=nkTakeawayScore(sentence,tokens,answer)-(sentence.length>240?1:0);
      if(score>bestScore){best=sentence;bestScore=score;}
    });
    const needed=tokens.length===1?1:2;
    return best&&bestScore>=needed?nkFinishTakeaway(best):nkFinishTakeaway(answer);
  }
/* NK_QUESTION_CONTENT_HYGIENE_V1_END */
