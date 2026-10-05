  /* NK_UWORLD_BIOCHEMISTRY_V1_START */
  function nkUworldLibraryCards(){
    return NK_UWORLD_COLLECTIONS.map(r=>{
    const available=r.questions.filter(nkUworldEligible),answered=available.filter(q=>qAttempts(q.id).length).length;
    const ready=available.length,pct=ready?Math.round(answered/ready*100):0;
    return `<button class="nk-v3-subject-card nk-uworld-collection" onclick="window.QB.openBank('${esc(r.subject)}','UWorld')"><span class="nk-v3-subject-icon">${nkSubjectGraphic(r.subject,24)}</span><span class="nk-v3-subject-copy"><strong>${esc(r.collection)}</strong><small>${fmtNum(r.topics.length)} ${r.topics.length===1?'block':'blocks'} · ${fmtNum(r.questions.length)} questions</small><span class="nk-v3-subject-progress"><i style="width:${pct}%"></i></span></span><b>${pct}%</b>${navIcon('chevron',18)}</button>`;
    }).join('');
  }
  function nkUworldHomeSection(){
    const collections=NK_UWORLD_COLLECTIONS.length,questions=NK_UWORLD_COLLECTIONS.reduce((total,r)=>total+r.questions.length,0);
    return `<section class="nk-v3-section nk-home-uworld" aria-label="My UWorld"><button class="nk-v3-subject-card nk-uworld-entry" aria-label="Open My UWorld" onclick="window.QB.nav('uworld')"><span class="nk-v3-subject-icon" aria-hidden="true">${navIcon('book',24)}</span><span class="nk-v3-subject-copy"><strong>My UWorld</strong><small>${fmtNum(collections)} ${collections===1?'collection':'collections'} · ${fmtNum(questions)} questions</small></span><span class="nk-uworld-entry-action" aria-hidden="true">Open</span>${navIcon('chevron',18)}</button></section>`;
  }
  function nkUworldLibraryPage(){return shell(`<main class="nk-app-v114 nk-uworld-library"><button class="nk-back-link" onclick="window.QB.nav('dashboard')">${navIcon('back',18)} Home</button><header class="nk-v3-page-hero"><h1>My UWorld</h1><p>Choose a collection, then open its original question blocks.</p></header><div class="nk-v3-subject-list">${nkUworldLibraryCards()}</div></main>`,'dashboard');}
  const nkUworldOriginalDashboard=dashboard;
  dashboard=function(){return nkUworldOriginalDashboard().replace('<section class="nk-home-progress">',nkUworldHomeSection()+'<section class="nk-home-progress">');};
  const nkUworldOriginalLibrary=nkStudyLibraryPage;
  nkStudyLibraryPage=function(){return nkUworldOriginalLibrary().replace('</main>',nkUworldHomeSection()+'</main>');};
  const nkUworldOriginalBankPage=bankPage;
  bankPage=function(name){return NK_UWORLD_COLLECTIONS.some(r=>r.subject===name)?nkUworldLibraryPage():nkUworldOriginalBankPage.apply(this,arguments);};
  const nkUworldOriginalTopicSection=nkTopicSection;
  nkTopicSection=function(chapter){return activeBank==='UWorld'?'Blocks':nkUworldOriginalTopicSection.apply(this,arguments);};
  const nkUworldOriginalTopics=topics;
  topics=function(){
    const out=nkUworldOriginalTopics.apply(this,arguments);if(activeBank!=='UWorld')return out;
    return out.replace(/<svg class="nk-topic-path"[\s\S]*?<\/svg>/g,'')
      .replaceAll('<span class="nk-topic-copy">','<span class="nk-uworld-topic-icon" aria-hidden="true">'+nkSubjectGraphic(activeSubject,24)+'</span><span class="nk-topic-copy">')
      .replace(/<div class="nk-subject-switch"[^>]*>[\s\S]*?<\/div>/,'')
      .replace(/aria-label="Back to question banks" onclick="[^"]*"/,'aria-label="Back to My UWorld" onclick="window.QB.nav(\'uworld\')"')
      .replace('<h1>'+esc(activeSubject)+'<small>','<h1>'+esc(nkBankRecord(activeSubject,'UWorld').collection)+'<small>')
      .replace('<h2>Topics</h2>','<h2>Blocks</h2>').replace('Choose a chapter and move directly into focused recall.','Choose a source block and move directly into focused recall.')
      .replace(/> topics</g,'> blocks<').replace(/<b>1<\/b> blocks/g,'<b>1</b> block').replaceAll(activeSubject+' · UWorld',activeSubject).replace('Topic index','Block index').replace('Search chapters or questions','Search blocks or questions');
  };
  const nkUworldOriginalChapterPage=chapterPage;
  chapterPage=function(){
    const out=nkUworldOriginalChapterPage.apply(this,arguments);
    return activeBank==='UWorld'?out.replace(/(class="nk-back-link"[^>]*>[\s\S]*?) Topics(<\/button>)/,'$1 Blocks$2'):out;
  };
  function nkUworldLegacyScope(draft){
    if(!draft)return draft;
    const translate=key=>{try{const parts=JSON.parse(key);if(parts[0]==='Biochemistry'&&parts[1]==='UWorld'){parts[0]=NK_UWORLD_BIOCHEMISTRY_BANK.subject;return JSON.stringify(parts);}}catch(_error){}return key;};
    return {...draft,scopeIds:draft.scopeIds?.map(translate),topicIds:draft.topicIds?.map(translate)};
  }
  const nkUworldOriginalModuleRecords=nkModuleSelectedRecords;
  nkModuleSelectedRecords=function(draft){return nkUworldOriginalModuleRecords(nkUworldLegacyScope(draft));};
  // Presentation adapter only. The incumbent engine owns answer commits and FSRS.
  function nkUworldAssetUrl(asset){return (location.hostname==='qbank.local'?'/app/':'./')+asset;}
  function nkUworldFigureMarkup(node,q,option=false){
    const caption=node.caption||'Source figure';
    const img=`<img src="${esc(nkUworldAssetUrl(node.asset))}" alt="${esc(caption)}" loading="eager" decoding="async" data-uworld-essential="${option||node.role==='question'?'true':'false'}" data-uworld-qid="${esc(q.id)}">`;
    if(option)return `<span class="nk-uworld-option-figure">${img}</span>`;
    return `<figure class="nk-uworld-figure"><button type="button" aria-label="Enlarge source figure" onclick="window.QB.uworldFigure('${esc(node.asset)}')">${img}<span>${navIcon('search',16)} Enlarge</span></button>${node.caption||node.source_note?`<figcaption>${nkScientificMarkup(node.caption||'')}${node.source_note?`<span class="nk-uworld-source-note">${nkScientificMarkup(node.source_note)}</span>`:''}</figcaption>`:''}</figure>`;
  }
  function nkUworldFigure(asset){
    const known=nkAllStudyQuestions().filter(q=>q.bank==='UWorld').some(q=>[...(q.uworldDocument?.question_blocks||[]),...(q.uworldDocument?.explanation||[]),...(q.options||[]).map(o=>o.figure)].some(n=>n?.asset===asset));
    if(known)window.NKSourceVisualViewer?.({type:'asset',source:asset},'UWorld source figure');
  }
  function nkUworldOptionMarkup(q,o){const text=String(o.text).trim()===o.letter?'Label '+o.letter:o.text;return nkScientificMarkup(text)+(o.figure?nkUworldFigureMarkup(o.figure,q,true):'');}
  function nkUworldParagraph(text){
    const label=String(text).match(/^(\(Choices?[^)]*\)|[1-9]\.\s+[A-Z][a-z]+:)(\s*)([\s\S]*)$/);
    return label?`<p><strong>${nkScientificMarkup(label[1])}</strong> ${nkScientificMarkup(label[3])}</p>`:`<p>${nkScientificMarkup(text)}</p>`;
  }
  function nkUworldTable(node){
    return `<figure class="nk-uworld-table">${node.caption?`<figcaption>${nkScientificMarkup(node.caption)}</figcaption>`:''}<div class="nk-uworld-table-scroll" role="region" aria-label="${esc(node.caption||'Source table')}" tabindex="0"><table><thead><tr>${node.columns.map(c=>`<th scope="col">${nkScientificMarkup(c)}</th>`).join('')}</tr></thead><tbody>${node.rows.map(row=>`<tr>${row.map((cell,i)=>i?`<td>${nkScientificMarkup(cell)}</td>`:`<th scope="row">${nkScientificMarkup(cell)}</th>`).join('')}</tr>`).join('')}</tbody></table></div></figure>`;
  }
  function nkUworldNodes(nodes,q){
    let discussion=false,heading=false;
    const out=[];
    const blocks=nodes||[];
    for(let index=0;index<blocks.length;index++){
      let node=blocks[index];
      // Some reviewed source paragraphs separate a choice label from its body.
      // Keep that source discussion together without changing archival records.
      if(node.type==='paragraph'&&/^\(Choices?\s+[^)]*\)\s*$/i.test(node.text)&&blocks[index+1]?.type==='paragraph'&&!/^\(Choices?\s+/i.test(blocks[index+1].text)){
        node={...node,text:node.text+' '+blocks[++index].text};
      }
      const choice=node.type==='paragraph'&&String(node.text).match(/^\(Choices?\s+([^)]*)\)\s*([\s\S]*)$/i);
      if(choice){
        if(!discussion){out.push(`<section class="nk-uworld-choices">${heading?'':'<h3>Understanding the other choices</h3>'}`);discussion=true;heading=true;}
        out.push(`<article class="nk-uworld-choice-discussion"><h4>${nkScientificMarkup('Choice'+(/^(?:[A-I])$/.test(choice[1])?'':'s')+' '+choice[1])}</h4><p>${nkScientificMarkup(choice[2])}</p></article>`);
      }else{
        if(discussion){out.push('</section>');discussion=false;}
        out.push(node.type==='table'?nkUworldTable(node):node.type==='figure'?nkUworldFigureMarkup(node,q):nkUworldParagraph(node.text));
      }
    }
    if(discussion)out.push('</section>');return out.join('');
  }
  function nkUworldOptionPercentage(q,o,revealed=true){
    const values=q.uworldDocument?q.uworldDocument.statistics.selection_percent:Object.fromEntries((q.uworldSource?.options||[]).map(item=>[item.label,item.selection_percent]));
    if(!Object.values(values).some(value=>value!=null))return '';
    // Reserve the same quiet column before/after answering; text never rewraps
    // just because source percentages become visible.
    if(!revealed)return '<span class="nk-uworld-percent-space" aria-hidden="true"></span>';
    const value=values[o.letter];
    return value==null?'<span class="nk-uworld-percent-space" aria-hidden="true"></span>':`<span class="nk-uworld-option-percent" aria-label="${esc(value)} percent of learners chose option ${esc(o.letter)}">${esc(value)}%</span>`;
  }
  function nkUworldStatistics(q){
    const value=(q.uworldDocument?.statistics||q.uworldSource?.statistics)?.answered_correctly_percent;
    return value==null?'':`<p class="nk-uworld-cohort"><strong>${esc(value)}% answered correctly</strong><span>Reported in the UWorld source</span></p>`;
  }
  function nkUworldReading(q){
    const doc=q.uworldDocument;
    if(!doc)return '<div class="nk-uworld-reading"><p class="nk-uworld-source-note">The source explanation is not available yet.</p></div>';
    const objective=doc.educational_objective;
    return `<div class="nk-uworld-reading">${nkUworldNodes(doc.explanation,q)}${objective?`<section class="nk-uworld-objective"><h3>Educational objective</h3><p>${nkScientificMarkup(objective)}</p></section>`:'<p class="nk-uworld-source-note">The educational objective is unavailable or clipped in the supplied source.</p>'}<details class="nk-uworld-original"><summary>Source details</summary><p class="nk-uworld-source-note">Source PDF · pages ${esc(doc.reviewed_pages.join(', '))}</p>${doc.issues?.length?`<p class="nk-uworld-source-note">${nkScientificMarkup(doc.issues.join(' '))}</p>`:''}</details></div>`;
  }
  const nkUworldOriginalStem=nkQuestionStemMarkup;
  nkQuestionStemMarkup=function(q){
    if(q?.bank!=='UWorld')return nkUworldOriginalStem(q);
    const imageOptions=(q.options||[]).filter(o=>o.figure);
    const tools=imageOptions.length?`<details class="nk-uworld-option-tools"><summary>Enlarge option diagrams</summary><div>${imageOptions.map(o=>`<button type="button" aria-label="Enlarge option ${esc(o.letter)}" onclick="window.QB.uworldFigure('${esc(o.figure.asset)}')">${esc(o.letter)} ${navIcon('search',16)}</button>`).join('')}</div></details>`:'';
    const displayQuestion=q.uworldDocument?{...q,question:q.uworldDocument.question}:q;
    return `<div class="nk-uworld-stem">${nkUworldOriginalStem(displayQuestion)}${nkUworldNodes(q.uworldDocument?.question_blocks,q)}${tools}</div>`;
  };
  const nkUworldOriginalSupport=nkStudySupport;
  nkStudySupport=function(q,timeMs,unattempted=false,renderedSource=''){
    if(q?.bank!=='UWorld')return nkUworldOriginalSupport(q,timeMs,unattempted,renderedSource);
    const time=unattempted?'<span>Not answered in this test</span>':`<span>Answered in <strong>${esc(nkFormatQuestionTime(timeMs||0))}</strong></span>`;
    return `<div class="nk-study-support is-uworld"><div class="nk-answer-time">${navIcon('clock',19)}${time}</div>${nkUworldStatistics(q)}<section class="nk-source-section nk-uworld-explanation"><header><div>${navIcon('book',19)}<strong>Explanation</strong></div><span>UWorld 2024${q.uworldDocument?' · Source reviewed':' · Source pending'}</span></header>${nkUworldReading(q)}</section></div>`;
  };
  function nkUworldRequiredAssets(q){return [...(q?.uworldDocument?.question_blocks||[]).filter(n=>n.type==='figure'),...(q?.options||[]).map(o=>o.figure).filter(Boolean)].map(n=>n.asset);}
  function nkUworldMediaReady(q){
    const required=nkUworldRequiredAssets(q);if(!required.length)return true;
    const images=[...document.querySelectorAll('img[data-uworld-essential="true"]')].filter(img=>img.dataset.uworldQid===String(q.id));
    return required.every(asset=>images.some(img=>img.getAttribute('src').split('?')[0].endsWith(asset)&&img.complete&&img.naturalWidth>0));
  }
  function nkUworldRefreshMedia(){
    const q=typeof nkCurrentQuestion==='function'?nkCurrentQuestion():null;if(q?.bank!=='UWorld'||!nkUworldRequiredAssets(q).length)return;
    const ready=nkUworldMediaReady(q),s=state.activeSession,answered=Boolean(s?.submitted?.[q.id]);
    document.querySelectorAll('.option-list button').forEach(button=>{
      if(!ready&&!answered&&!button.disabled){button.disabled=true;button.dataset.uworldWaiting='true';}
      else if(ready&&button.dataset.uworldWaiting){button.disabled=false;delete button.dataset.uworldWaiting;}
    });
    const stem=document.querySelector('.nk-uworld-stem');if(!stem)return;
    let status=stem.querySelector('.nk-uworld-media-status');
    if(ready){status?.remove();return;}
    if(!status){status=document.createElement('span');status.className='nk-uworld-media-status';status.setAttribute('role','status');stem.append(status);}
    const failed=[...document.querySelectorAll('img[data-uworld-essential="true"]')].some(img=>img.dataset.uworldQid===String(q.id)&&img.complete&&!img.naturalWidth);
    const message=failed?`The source figure could not load. <button type="button" onclick="window.QB.uworldRetryFigures()">Retry figures</button>`:'Loading the source figure needed to answer this question…';
    if(status.innerHTML!==message)status.innerHTML=message;
  }
  function nkUworldRetryFigures(){document.querySelectorAll('img[data-uworld-qid]').forEach(img=>{if(!img.naturalWidth)img.src=img.getAttribute('src').split('?')[0]+'?retry='+Date.now();});nkUworldRefreshMedia();}
  const nkUworldOriginalValidOption=nkValidQuestionOption;
  nkValidQuestionOption=function(q,n){
    if(!nkUworldOriginalValidOption(q,n))return false;
    const s=state.activeSession,current=s?.questionIds?.[s.index];
    return q?.bank!=='UWorld'||String(current)!==String(q.id)||Boolean(s.submitted?.[q.id])||nkUworldMediaReady(q);
  };
  const nkUworldOriginalRender=render;
  render=function(){const out=nkUworldOriginalRender.apply(this,arguments);nkUworldRefreshMedia();return out;};
  if(typeof document!=='undefined')for(const event of ['load','error'])document.addEventListener(event,e=>{if(e.target?.matches?.('img[data-uworld-qid]'))nkUworldRefreshMedia();},true);
  function nkUworldEligible(q){return q?.bank!=='UWorld'||nkQuestionPresentationFor(q).valid;}
  // Filter before sampling, so new tests/modules have accurate counts and full sets.
  const nkUworldOriginalChapterStats=chapterStats;
  chapterStats=function(cid){
    if(activeBank!=='UWorld')return nkUworldOriginalChapterStats.apply(this,arguments);
    const qs=chapterQuestions(cid).filter(nkUworldEligible),attempts=qs.flatMap(q=>qAttempts(q.id));
    const correct=attempts.filter(a=>a.correct).length,incorrect=attempts.filter(a=>!a.correct).length;
    return {total:qs.length,attempted:qs.filter(q=>qAttempts(q.id).length).length,correct,incorrect,accuracy:correct+incorrect?correct/(correct+incorrect)*100:0};
  };
  const nkUworldCbtPool=nkCbtPool;
  nkCbtPool=function(){return nkUworldCbtPool.apply(this,arguments).filter(nkUworldEligible);};
  const nkUworldModulePool=nkQuestionsForModuleDraft;
  nkQuestionsForModuleDraft=function(){return nkUworldModulePool(nkUworldLegacyScope(arguments[0]===undefined?studyModuleDraft:arguments[0])).filter(nkUworldEligible);};
  const nkUworldRevisionData=nkRevisionDeskData;
  nkRevisionDeskData=function(){
    const data=nkUworldRevisionData.apply(this,arguments);
    for(const key of ['wrong','bookmarked','unseen','due','dueCards'])data[key]=(data[key]||[]).filter(nkUworldEligible);
    return data;
  };
  const nkUworldStartSession=startSession;
  startSession=function(ids){
    const questions=new Map(nkAllStudyQuestions().map(q=>[String(q.id),q]));
    const eligible=(ids||[]).filter(id=>nkUworldEligible(questions.get(String(id))));
    if(!eligible.length&&ids?.length){showToast('These questions need source diagrams. Open them individually to read the available explanation.','bad');return false;}
    const args=[...arguments];args[0]=eligible;return nkUworldStartSession.apply(this,args);
  };
  function nkUworldReference(id){
    const q=nkFindStudyQuestion(id);if(q?.bank!=='UWorld'||nkUworldEligible(q))return false;
    if(state.activeSession?.mode==='exam'){showToast('Finish or leave your timed test before opening another question.','bad');return false;}
    closeModal();
    document.body.insertAdjacentHTML('beforeend',`<div class="modal-backdrop nk-modal-v114" id="modal"><section class="modal nk-uworld-reference" role="dialog" aria-modal="true" aria-labelledby="nk-uworld-reference-title"><button type="button" class="nk-modal-close" aria-label="Close" onclick="window.QB.closeModal()">${navIcon('close',20)}</button><h2 id="nk-uworld-reference-title">Diagram needed</h2><p class="nk-uworld-source-note">This question is reference only until its source diagram is added. Reading it does not record an answer or affect your score.</p><div class="nk-uworld-reference-question">${nkScientificMarkup(q.question)}</div><details class="nk-uworld-reference-explanation"><summary>Read explanation</summary>${nkUworldReading(q)}</details></section></div>`);
    return true;
  }
  const nkUworldPracticeOne=practiceOne;
  practiceOne=function(id){const q=nkFindStudyQuestion(id);return q?.bank==='UWorld'&&!nkUworldEligible(q)?nkUworldReference(id):nkUworldPracticeOne.apply(this,arguments);};
  /* NK_UWORLD_BIOCHEMISTRY_V1_END */
