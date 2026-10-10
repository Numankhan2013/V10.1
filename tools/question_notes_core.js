  /* NK_QUESTION_NOTES_V1_START */
  const NK_NOTE_MEDIA_LIMIT=10,NK_NOTE_TEXT_LIMIT=10;
  const NK_NOTE_ASSET_ID=/^na_[a-z0-9_]{6,60}$/,NK_NOTE_MIME=['image/jpeg','image/png','image/webp'];
  function nkNoteMediaBlock(block){return Boolean(block&&block.type==='image'&&block.asset&&NK_NOTE_ASSET_ID.test(String(block.asset.id||'')));}
  function nkNoteSanitizeBlocks(value){
    if(!Array.isArray(value))return [];
    const out=[];let media=0,texts=0;
    for(const block of value.slice(0,40)){
      if(block&&block.type==='text'&&typeof block.text==='string'){
        const text=block.text.replace(/\r\n?/g,'\n').slice(0,2000);
        if(text.trim()&&texts<NK_NOTE_TEXT_LIMIT){out.push({type:'text',text});texts++;}
      }else if(nkNoteMediaBlock(block)&&media<NK_NOTE_MEDIA_LIMIT){
        const a=block.asset,mime=NK_NOTE_MIME.includes(a.mime)?a.mime:'image/jpeg';
        out.push({type:'image',source:block.source==='pdf'?'pdf':'image',label:String(block.label||'').slice(0,120),
          asset:{id:String(a.id),mime,w:Math.max(1,Math.round(Number(a.w)||1)),h:Math.max(1,Math.round(Number(a.h)||1)),bytes:Math.max(0,Math.round(Number(a.bytes)||0))}});
        media++;
      }
    }
    return out;
  }
  // A note is ordered text and image parts. Older notes and older app versions only know `text`.
  function nkNoteBlocks(note){
    if(!note||note.deleted)return [];
    const text=typeof note.text==='string'?note.text:'';
    if(!Array.isArray(note.blocks))return text.trim()?[{type:'text',text}]:[];
    const blocks=nkNoteSanitizeBlocks(note.blocks);
    // An older app version edited the text after these parts were saved: keep its text and the images.
    if(Number(note.blocksAt||0)<Number(note.updatedAt||0))return [...(text.trim()?[{type:'text',text}]:[]),...blocks.filter(nkNoteMediaBlock)];
    return blocks;
  }
  function nkNoteSummary(blocks){return blocks.filter(block=>block.type==='text').map(block=>block.text).join('\n\n').slice(0,2000);}
  function nkQuestionNote(id){
    const record=state.questionNotes?.[String(id)];
    return record&&!record.deleted&&nkNoteBlocks(record).length?record:null;
  }

  function nkSaveQuestionNoteBlocks(id,value){
    const qid=String(id);
    if(!BY_ID[qid]||!Array.isArray(value))return false;
    const cleaned=value.map(block=>block?.type==='text'?{type:'text',text:String(block.text||'').replace(/\r\n?/g,'\n').trim()}:block);
    if(cleaned.some(block=>block?.type==='text'&&block.text.length>2000))return false;
    const blocks=nkNoteSanitizeBlocks(cleaned);
    const notes=state.questionNotes||(state.questionNotes={}),previous=notes[qid],before=nkNoteBlocks(previous);
    if(JSON.stringify(before)===JSON.stringify(blocks))return true;
    const updatedAt=Math.max(Date.now(),Number(previous?.updatedAt||0)+1),deleted=!blocks.length;
    const next={text:nkNoteSummary(blocks),updatedAt,deleted};
    // Once a note has parts it keeps writing them, so another device cannot resurrect removed images.
    if(blocks.some(nkNoteMediaBlock)||Array.isArray(previous?.blocks)){next.blocks=blocks;next.blocksAt=updatedAt;}
    notes[qid]=next;
    if(!saveState()){
      if(previous===undefined)delete notes[qid];else notes[qid]=previous;
      return false;
    }
    const kept=blocks.filter(nkNoteMediaBlock).map(block=>block.asset.id),keep=new Set(kept);
    const removed=before.filter(block=>nkNoteMediaBlock(block)&&!keep.has(block.asset.id)).map(block=>block.asset);
    if(typeof nkNoteAssetsCommit==='function'&&(kept.length||removed.length))nkNoteAssetsCommit(kept,removed);
    showToast(deleted?'Note removed.':'Note saved.','good');
    return true;
  }

  function nkSaveQuestionNote(id,value){
    const text=String(value||'').replace(/\r\n?/g,'\n').trim();
    if(text.length>2000)return false;
    return nkSaveQuestionNoteBlocks(id,text?[{type:'text',text}]:[]);
  }

  function nkSavedQuestionNotes(){
    const questions=typeof nkAllBankQuestions==='function'?nkAllBankQuestions():nkAllStudyQuestions();
    const byId=new Map(questions.map(q=>[String(q.id),q]));
    return Object.entries(state.questionNotes||{}).flatMap(([id,note])=>
      nkNoteBlocks(note).length?[{id,note,q:byId.get(id)||null}]:[]
    ).sort((a,b)=>Number(b.note.updatedAt||0)-Number(a.note.updatedAt||0));
  }

  let nkNotesQuery="";
  function nkNotesPage(){
    const entries=nkSavedQuestionNotes();
    return shell(`<div class="nk-app-v114 nk-notes-page">${nkAppPageHead('PERSONAL REVISION','My notes','Recall cues saved while reviewing questions.')}
      <div class="nk-notes-count">${fmtNum(entries.length)} saved note${entries.length===1?'':'s'}</div>
      ${entries.length?`<label class="nk-notes-search"><span aria-hidden="true">${navIcon('search',20)}</span><input type="search" value="${esc(nkNotesQuery)}" placeholder="Search notes or questions" aria-label="Search notes or questions" oninput="window.QB.nkFilterNotes(this.value)"></label>
      <div class="nk-notes-list">${entries.map(({id,note,q})=>{
        const subject=q?.subject||'Question unavailable',bank=q?.bank||'',topic=q?.chapter||q?.topic||'';
        const blocks=nkNoteBlocks(note),text=blocks.filter(block=>block.type==='text').map(block=>block.text).join('\n\n'),media=blocks.filter(nkNoteMediaBlock);
        const key=encodeURIComponent(id),search=esc(`${subject} ${bank} ${topic} ${q?.question||''} ${text}`.toLowerCase());
        const strip=media.length&&typeof nkNoteMediaFrame==='function'?`<div class="nk-notes-item-media" aria-label="${media.length} image${media.length===1?'':'s'} in this note">${media.slice(0,4).map(block=>nkNoteMediaFrame(block,'thumb')).join('')}${media.length>4?`<span class="nk-notes-item-more">+${media.length-4}</span>`:''}</div>`:'';
        return `<article class="nk-notes-item" data-note-search="${search}"><div class="nk-notes-item-meta">${esc(subject)}${bank?` · ${esc(bank)}`:''}${topic?` · ${esc(topic)}`:''}</div><p class="nk-notes-item-question">${q?esc(q.question):'This question is not in the current banks.'}</p>${text?`<div class="nk-notes-item-text">${esc(text)}</div>`:''}${strip}${q?`<button type="button" onclick="window.QB.nkOpenNotedQuestion('${key}')">Practice question ${navIcon('chevron',16)}</button>`:''}</article>`;
      }).join('')}</div><p class="nk-notes-no-match" role="status" hidden>No notes match your search.</p>`:
      nkAppEmpty('book','No notes yet','After answering a question, add a recall cue below the answer. It will appear here.')}
    </div>`,'more');
  }

  function nkFilterNotes(value){
    nkNotesQuery=String(value||'');
    const term=nkNotesQuery.trim().toLowerCase();
    let shown=0;
    document.querySelectorAll('.nk-notes-item').forEach(item=>{
      item.hidden=Boolean(term)&&!item.dataset.noteSearch.includes(term);
      if(!item.hidden)shown++;
    });
    const empty=document.querySelector('.nk-notes-no-match');
    if(empty)empty.hidden=shown>0;
  }

  function nkOpenNotedQuestion(encodedId){
    let id;try{id=decodeURIComponent(encodedId)}catch{return;}
    const entry=nkSavedQuestionNotes().find(item=>item.id===id);
    if(!entry?.q){showToast('This question is unavailable.','bad');return;}
    if(state.activeSession?.mode==='exam'){
      showToast('Finish or leave your timed test before practicing a noted question.','bad');
      return;
    }
    const q=entry.q;
    if(typeof openBank==='function'&&q.subject&&q.bank)openBank(q.subject,q.bank);
    BY_ID={...BY_ID,[id]:q};
    const previous=state.activeSession?.id;
    practiceOne(id);
    if(state.activeSession?.id!==previous&&state.activeSession?.questionIds?.[0]===id){
      state.activeSession.originRoute='notes';saveState();
    }
  }

  let nkNoteDraftOwner="",nkNotesAccount="";
  const nkNoteDrafts=new Map();
  function nkNoteDraft(value){
    if(typeof value==='string')return {blocks:[{type:'text',text:value}],added:new Set()};
    return value&&Array.isArray(value.blocks)?value:{blocks:[{type:'text',text:''}],added:new Set()};
  }
  function nkNoteBlocksMarkup(blocks){
    let media=0;
    return blocks.map(block=>{
      if(block.type==='text')return `<div class="nk-note-readonly">${esc(block.text)}</div>`;
      if(typeof nkNoteMediaFrame!=='function')return '';
      const label=block.label||(block.source==='pdf'?'PDF page':'Image');
      return `<figure class="nk-note-figure"><button type="button" class="nk-note-figure-open" data-nk-note-open="${media++}" aria-label="Open ${esc(label)} full screen">${nkNoteMediaFrame(block,'preview')}</button>${block.label?`<figcaption>${esc(block.label)}</figcaption>`:''}</figure>`;
    }).join('');
  }

  function nkMountQuestionNote(){
    const account=String(typeof nkAuth!=="undefined"&&nkAuth?.uid||"local");
    if(account!==nkNotesAccount){nkNotesQuery="";nkNotesAccount=account;}
    const owner=account+":"+String(state.activeSession?.id||"");
    if(owner!==nkNoteDraftOwner){nkNoteDrafts.clear();nkNoteDraftOwner=owner;}
    const page=route.page;
    if(page==='notes'){nkFilterNotes(nkNotesQuery);if(typeof nkNoteHydrate==='function')nkNoteHydrate(document.querySelector('.nk-notes-page'));return;}
    if(page!=='practice'&&page!=='review-test')return;
    const session=state.activeSession,qid=String(session?.questionIds?.[session.index]||'');
    if(!BY_ID[qid]||(page==='practice'&&!session?.submitted?.[qid]))return;
    const card=document.querySelector('.question-card');if(!card)return;
    const section=document.createElement('section');
    section.className='nk-question-note';
    const source=card.querySelector('.nk-source-section');
    const feedback=card.querySelector('.feedback,.nk-practice-response');
    if(source)source.insertAdjacentElement('beforebegin',section);
    else if(feedback)feedback.insertAdjacentElement('beforebegin',section);
    else card.appendChild(section);
    let draft=null,busy=false;

    function savedAssetIds(){return new Set(nkNoteBlocks(state.questionNotes?.[qid]).filter(nkNoteMediaBlock).map(block=>block.asset.id));}
    function discardDraft(){
      if(draft&&typeof nkNoteDiscardDraftAssets==='function'){const saved=savedAssetIds();nkNoteDiscardDraftAssets([...draft.added].filter(id=>!saved.has(id)));}
      nkNoteDrafts.delete(qid);draft=null;
    }

    function showReadOnly(focus=false){
      draft=null;
      const note=nkQuestionNote(qid);
      if(!note){
        section.innerHTML='<div class="nk-question-note-head"><div><strong>My note</strong><small>Add a point to remember</small></div><button type="button" class="nk-note-add">Add note</button></div>';
        section.querySelector('.nk-note-add').addEventListener('click',()=>showEditor(nkNoteDraft('')));
        if(focus)section.querySelector('.nk-note-add').focus();
        return;
      }
      const blocks=nkNoteBlocks(note),media=blocks.filter(nkNoteMediaBlock).length;
      section.innerHTML=`<div class="nk-question-note-head"><div><strong>My note</strong><small>Saved for this question</small></div><div class="nk-note-tools"><button type="button" class="nk-note-edit" aria-label="Edit note">Edit</button><button type="button" class="nk-note-delete" aria-label="Delete note">Delete</button></div></div><div class="nk-note-blocks">${nkNoteBlocksMarkup(blocks)}</div>`;
      section.querySelector('.nk-note-edit').addEventListener('click',()=>showEditor({blocks:blocks.map(block=>({...block})),added:new Set()}));
      section.querySelector('.nk-note-delete').addEventListener('click',()=>{
        if(media&&!confirm(`Delete this note and its ${media} image${media===1?'':'s'}?`))return;
        if(nkSaveQuestionNoteBlocks(qid,[]))showReadOnly(true);
        else showToast('Could not delete the note. Please try again.','bad');
      });
      section.querySelectorAll('[data-nk-note-open]').forEach(button=>button.addEventListener('click',()=>{if(typeof nkNoteOpenViewer==='function')nkNoteOpenViewer(blocks,Number(button.dataset.nkNoteOpen));}));
      if(typeof nkNoteHydrate==='function')nkNoteHydrate(section);
      if(focus)section.querySelector('.nk-note-edit').focus();
    }

    function showEditor(value,focus=true,focusIndex=0){
      draft=nkNoteDraft(value);
      const blocks=draft.blocks,mediaCount=blocks.filter(nkNoteMediaBlock).length,textCount=blocks.filter(block=>block.type==='text').length;
      const mediaReady=typeof nkNoteImportImage==='function';
      let firstText=true;
      const parts=blocks.map((block,index)=>{
        const tools=blocks.length>1?`<div class="nk-note-part-tools"><button type="button" data-note-act="up" data-i="${index}" aria-label="Move part up"${index===0?' disabled':''}>↑</button><button type="button" data-note-act="down" data-i="${index}" aria-label="Move part down"${index===blocks.length-1?' disabled':''}>↓</button><button type="button" data-note-act="remove" data-i="${index}" aria-label="Remove part">Remove</button></div>`:'';
        if(block.type==='text'){
          const first=firstText;firstText=false;
          return `<div class="nk-note-part is-text">${first?'<label for="nk-question-note-text">Your own words</label>':''}<textarea${first?' id="nk-question-note-text"':' aria-label="Note text"'} data-i="${index}" maxlength="2000" rows="4" placeholder="Write the idea you want to recall later.">${esc(block.text)}</textarea>${tools}</div>`;
        }
        return `<div class="nk-note-part is-media">${typeof nkNoteMediaFrame==='function'?nkNoteMediaFrame(block,'thumb'):''}<div class="nk-note-part-label">${esc(block.label||(block.source==='pdf'?'PDF page':'Image'))}</div>${tools}</div>`;
      }).join('');
      const addRow=mediaReady?`<div class="nk-note-add-row" role="group" aria-label="Add to this note"><button type="button" data-note-act="add-text" aria-label="Add text part"${textCount>=NK_NOTE_TEXT_LIMIT?' disabled':''}>+ Text</button><button type="button" data-note-act="add-image" aria-label="Add image"${mediaCount>=NK_NOTE_MEDIA_LIMIT?' disabled':''}>+ Image</button><button type="button" data-note-act="add-pdf" aria-label="Add PDF pages"${mediaCount>=NK_NOTE_MEDIA_LIMIT?' disabled':''}>+ PDF pages</button><input type="file" class="nk-note-file nk-note-file-image" accept="image/*" multiple tabindex="-1" aria-hidden="true"><input type="file" class="nk-note-file nk-note-file-pdf" accept="application/pdf,.pdf" tabindex="-1" aria-hidden="true"></div>`:'';
      const hint=mediaCount?`${mediaCount} of ${NK_NOTE_MEDIA_LIMIT} images or pages`:'Up to 2,000 characters';
      section.innerHTML=`<div class="nk-question-note-head"><div><strong>My note</strong><small>${nkQuestionNote(qid)?'Edit your recall cue':'Add a point to remember'}</small></div></div><div class="nk-question-note-body"><div class="nk-note-parts">${parts}</div>${addRow}<div class="nk-question-note-actions"><small role="status">${hint}</small><div><button type="button" class="nk-note-cancel">Cancel</button><button type="button" class="nk-note-save">Save note</button></div></div></div>`;
      const status=section.querySelector('[role="status"]');
      nkNoteDrafts.set(qid,draft);
      section.querySelectorAll('textarea').forEach(input=>input.addEventListener('input',()=>{
        const block=draft.blocks[Number(input.dataset.i)];if(block)block.text=input.value;
        nkNoteDrafts.set(qid,draft);status.textContent='Draft kept for this session. Save to keep it.';
      }));
      if(!focus)status.textContent='Draft kept for this session. Save to keep it.';
      section.querySelector('.nk-question-note-body').addEventListener('click',event=>{
        const button=event.target.closest('[data-note-act]');if(!button||button.disabled||busy)return;
        const act=button.dataset.noteAct,index=Number(button.dataset.i);
        if(act==='up'||act==='down'){
          const target=act==='up'?index-1:index+1;if(target<0||target>=draft.blocks.length)return;
          [draft.blocks[index],draft.blocks[target]]=[draft.blocks[target],draft.blocks[index]];
          showEditor(draft,false);section.querySelector(`[data-note-act="${act}"][data-i="${target}"]:not([disabled])`)?.focus({preventScroll:true});
        }else if(act==='remove'){
          draft.blocks.splice(index,1);if(!draft.blocks.length)draft.blocks.push({type:'text',text:''});
          showEditor(draft,false);
        }else if(act==='add-text'){
          draft.blocks.push({type:'text',text:''});showEditor(draft,false);
          const inputs=section.querySelectorAll('textarea');inputs[inputs.length-1]?.focus({preventScroll:false});
        }else if(act==='add-image')section.querySelector('.nk-note-file-image')?.click();
        else if(act==='add-pdf')section.querySelector('.nk-note-file-pdf')?.click();
      });
      section.querySelectorAll('input[type="file"]').forEach(input=>input.addEventListener('change',()=>{const files=[...(input.files||[])];input.value='';importFiles(files);}));
      section.querySelector('.nk-note-cancel').addEventListener('click',()=>{if(busy)return;discardDraft();showReadOnly(true);});
      section.querySelector('.nk-note-save').addEventListener('click',()=>{
        if(busy)return;
        const blocks=draft.blocks.filter(block=>block.type!=='text'||block.text.trim());
        if(!blocks.length){status.textContent='Write a note before saving.';return;}
        if(!nkSaveQuestionNoteBlocks(qid,blocks)){
          status.textContent='Save failed. Your text is still here.';
          return;
        }
        discardDraft();
        showReadOnly(true);
      });
      if(typeof nkNoteHydrate==='function')nkNoteHydrate(section);
      if(focus){const input=section.querySelectorAll('textarea')[focusIndex]||section.querySelector('textarea');input?.focus({preventScroll:true});section.scrollIntoView({block:"center",behavior:"instant"});}
    }

    async function importFiles(files){
      if(!draft||busy||!files.length||typeof nkNoteImportImage!=='function')return;
      const status=section.querySelector('[role="status"]'),working=draft;
      busy=true;section.querySelectorAll('[data-note-act],.nk-note-save').forEach(button=>{button.disabled=true;});
      try{
        for(const file of files){
          const remaining=NK_NOTE_MEDIA_LIMIT-working.blocks.filter(nkNoteMediaBlock).length;
          if(remaining<=0){showToast(`A note holds up to ${NK_NOTE_MEDIA_LIMIT} images or pages.`,'bad');break;}
          const pdf=/pdf$/i.test(file.type||'')||/\.pdf$/i.test(file.name||'');
          if(status)status.textContent=pdf?'Opening PDF…':'Adding image…';
          const added=pdf?await nkNoteImportPdf(file,remaining,text=>{if(status)status.textContent=text;}):[await nkNoteImportImage(file)];
          // An empty first text box gives way so a screenshot-only note starts with the image.
          if(working.blocks.length===1&&working.blocks[0].type==='text'&&!working.blocks[0].text.trim()&&added.length)working.blocks.splice(0,1);
          added.forEach(block=>{working.blocks.push(block);working.added.add(block.asset.id);});
        }
      }catch(error){showToast(String(error?.message||error||'Could not add this file.'),'bad');}
      finally{busy=false;}
      nkNoteDrafts.set(qid,working);
      if(section.isConnected&&draft===working)showEditor(working,false);
    }

    section.addEventListener('paste',event=>{
      if(!draft)return;
      const files=[...(event.clipboardData?.files||[])].filter(file=>/^image\//.test(file.type||''));
      if(!files.length)return;
      event.preventDefault();importFiles(files);
    });
    section.addEventListener('dragover',event=>{if(draft&&[...(event.dataTransfer?.types||[])].includes('Files'))event.preventDefault();});
    section.addEventListener('drop',event=>{
      if(!draft)return;
      const files=[...(event.dataTransfer?.files||[])];if(!files.length)return;
      event.preventDefault();importFiles(files);
    });
    if(nkNoteDrafts.has(qid))showEditor(nkNoteDrafts.get(qid),false);
    else showReadOnly();
  }
  /* NK_QUESTION_NOTES_V1_END */
