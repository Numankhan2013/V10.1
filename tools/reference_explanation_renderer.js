  function richText(text) {
    return esc(String(text||'')).replace(/\*\*(.*?)\*\*/g,'<strong>$1</strong>');
  }

  function splitSourceParagraphs(text){
    const lines=String(text||'').replace(/\r/g,'').split('\n');
    const chunks=[]; let cur=[]; let bullet=false;
    const flush=()=>{if(cur.length){chunks.push(cur.join(' ').replace(/\s+/g,' ').trim());cur=[];bullet=false;}};
    const heading=/^(Algorithm|Investigations|Significance|Mechanism|Key point|Recognition|Cause|Regulation|Identification Tips|Other options|Correct Option|Simple carbohydrates|Polysaccharides|Locations of Various)\s*:?\s*$/i;
    lines.forEach(line=>{
      const t=line.trim();
      if(!t){flush();return;}
      if(heading.test(t)){flush();chunks.push(t);return;}
      if(/^•\s*/.test(t) || /^[-–—]\s+/.test(t)){flush();cur=[t];bullet=true;return;}
      if(bullet){cur.push(t);return;}
      cur.push(t);
    });
    flush();
    return chunks.filter(Boolean);
  }

  function parseOptionBlocks(text, question){
    const sourceOptions=Array.isArray(question?.options)?question.options:[];
    const raw=String(text||'').replace(/\r/g,'').trim();
    const headingMatch=/\b(Other options|Incorrect Options|Incorrect Option|Incorrect Choices)\s*:\s*/i.exec(raw);
    if(!headingMatch) return {pre:raw,items:[],heading:''};
    const pre=raw.slice(0,headingMatch.index).trim();
    const optionText=raw.slice(headingMatch.index+headingMatch[0].length).trim();
    const marker=/(?:\(\s*Option\s+([A-E])\s*\)|\bOption\s+([A-E])\s*[-:])/ig;
    const markers=[...optionText.matchAll(marker)];
    if(!markers.length) return {pre,items:[],heading:headingMatch[1]};
    const items=[];
    for(let i=0;i<markers.length;i++){
      const m=markers[i], letter=(m[1]||m[2]).toUpperCase();
      const segEnd=i<markers.length-1?markers[i+1].index:optionText.length;
      let after=optionText.slice(m.index+m[0].length,segEnd).trim();
      const opt=sourceOptions.find(o=>String(o.letter).toUpperCase()===letter);
      const title=opt?.text||`Option ${letter}`;
      const titleRx=new RegExp('^'+title.replace(/[.*+?^${}()|[\\]\\]/g,'\\$&')+'\\s*[:\\-–—]?\\s*','i');
      after=after.replace(titleRx,'').trim();
      if(i<markers.length-1){
        const nextLetter=(markers[i+1][1]||markers[i+1][2]).toUpperCase();
        const nextOpt=sourceOptions.find(o=>String(o.letter).toUpperCase()===nextLetter);
        if(nextOpt){const nextTitle=String(nextOpt.text||'').trim();const trailRx=new RegExp('\\s*'+nextTitle.replace(/[.*+?^${}()|[\\]\\]/g,'\\$&')+'\\s*$','i');after=after.replace(trailRx,'').trim();}
      }
      items.push({letter,title,body:after});
    }
    return {pre,items,heading:headingMatch[1]};
  }

  function parseSourceTable(text){
    const lines=String(text||'').replace(/\r/g,'').split('\n');
    for(let h=0;h<Math.min(lines.length,30);h++){
      const line=lines[h]; const runs=[...line.matchAll(/\s{4,}/g)]; if(runs.length<1) continue;
      const positions=[0,...runs.map(r=>r.index+r[0].length)]; const heads=line.split(/\s{4,}/).map(x=>x.trim()).filter(Boolean); if(heads.length<2)continue;
      const looksLikeRow=(l)=>{if(!l.trim())return false;const lead=(l.match(/^\s*/)||[''])[0].length;if(lead>0&&positions.some(p=>Math.abs(p-lead)<=2))return true;return /\s{4,}/.test(l);};
      let i=h+1,rowBlocks=[],cur=[],boundary=false;const flush=()=>{if(cur.length){rowBlocks.push(cur);cur=[];}};
      for(;i<lines.length;i++){const l=lines[i];if(!l.trim()){flush();boundary=true;continue;}if(/^(Other options|Incorrect Options|Incorrect Option|Incorrect Choices)\s*:/i.test(l.trim())){flush();break;}if(boundary&&rowBlocks.length&&!looksLikeRow(l))break;boundary=false;cur.push(l);}flush();
      const rows=[];for(const block of rowBlocks){const first=block[0],cells=[];for(let c=0;c<positions.length;c++){const aa=positions[c],bb=c+1<positions.length?positions[c+1]:first.length;cells.push(first.slice(aa,bb).trim());}for(const cont of block.slice(1)){for(let c=0;c<positions.length;c++){const piece=cont.slice(positions[c],c+1<positions.length?positions[c+1]:cont.length).trim();if(piece)cells[c]=(cells[c]?cells[c]+' ':'')+piece;}}if(cells.some(Boolean))rows.push(cells);}if(rows.length)return {heads,rows,startLine:h,consumedLines:i};
    }
    return null;
  }

  function renderSourceTable(table){
    const head=table.heads||[], rows=table.rows||[];
    return `<div class="source-table-card" role="table" aria-label="Source explanation table"><div class="source-table-desktop" style="--table-cols:${head.length}"><div class="source-table-head">${head.map(h=>`<div>${richText(h)}</div>`).join('')}</div>${rows.map(r=>`<div class="source-table-row">${head.map((h,j)=>`<div class="${j===0?'row-label':''}">${richText(r[j]||'')}</div>`).join('')}</div>`).join('')}</div><div class="source-table-mobile">${rows.map(r=>`<article class="source-table-mobile-row">${head.map((h,j)=>`<div class="source-table-mobile-cell"><span class="source-table-mobile-label">${richText(h)}</span><span class="source-table-mobile-value ${j===0?'row-label':''}">${richText(r[j]||'')}</span></div>`).join('')}</article>`).join('')}</div></div>`;
  }

  function renderOptionReview(items,question){
    const correct=Number(question?.correctOption||0);
    return `<div class="explain-section-title option-review-title">Option-by-option review</div><div class="explain-option-list">${items.map(x=>{const isCorrect=Number(x.letter.charCodeAt(0)-64)===correct;return `<article class="explain-option-item ${isCorrect?'fits':''}"><div class="explain-option-head"><span class="explain-tag">Option ${x.letter}</span><span>${richText(x.title)}</span></div><div class="explain-option-reason">${isCorrect?'Why it fits':'Why it doesn’t fit'}</div><div class="explain-option-body">${richText(x.body||'The supplied source does not provide a separate reason for this option.')}</div></article>`;}).join('')}</div>`;
  }

  function renderPlainExplanation(text){
    if(!text)return '';
    return splitSourceParagraphs(text).map(p=>{if(/^•\s*/.test(p))return `<div class="explain-bullet"><span class="bullet-dot">•</span><div>${richText(p.replace(/^•\s*/,''))}</div></div>`;if(/^(Algorithm|Investigations|Significance|Mechanism|Key point|Recognition|Cause|Regulation|Identification Tips|Other options|Correct Option|Simple carbohydrates|Polysaccharides|Locations of Various)\s*:?\s*$/i.test(p))return `<div class="explain-section-title">${richText(p.replace(/:$/,''))}</div>`;return `<p class="explain-paragraph">${richText(p)}</p>`;}).join('');
  }

  function renderExplanationText(text,question){
    if(!text)return '';
    let normalized=String(text).replace(/\r/g,'').trim();
    normalized=normalized.replace(/^(?:Correct\s+(?:Answer|answer)|Answer|Correct\s+Option)\s*[:\-]?\s*[A-E]\)?[\s\S]*?(?=\n\s*(?:Explanation\s*:|•|Incorrect Options\s*:|Other options\s*:)|$)/i,'');
    normalized=normalized.replace(/^\s*(?:Explanation\s*:\s*)/i,'').trim();
    const optionData=parseOptionBlocks(normalized,question),mainText=optionData.pre,blocks=[]; const table=parseSourceTable(mainText);
    if(table){const lines=mainText.split('\n'),intro=lines.slice(0,table.startLine).join('\n').trim();if(intro)blocks.push(renderPlainExplanation(intro));blocks.push(renderSourceTable(table));const remainder=lines.slice(table.consumedLines).join('\n').trim();if(remainder)blocks.push(renderPlainExplanation(remainder));}else blocks.push(renderPlainExplanation(mainText));
    if(optionData.items.length)blocks.push(renderOptionReview(optionData.items,question));
    return blocks.filter(Boolean).join('');
  }
