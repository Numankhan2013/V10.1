  /* NK_QUESTION_NOTES_V1_START */
  const NK_NOTE_MEDIA_LIMIT=10,NK_NOTE_TEXT_LIMIT=10,NK_NOTE_AUDIO_LIMIT=5;
  const NK_NOTE_ASSET_ID=/^na_[a-z0-9_]{6,60}$/,NK_NOTE_MIME=['image/jpeg','image/png','image/webp'];
  // Voice clips keep the container type only (codecs are read from the bytes); 10 minutes is a safe ceiling for imports.
  const NK_NOTE_AUDIO_MIME=/^audio\/[a-z0-9.+-]{1,30}$/,NK_NOTE_AUDIO_MAX_MS=600000;
  function nkNoteMediaBlock(block){return Boolean(block&&block.type==='image'&&block.asset&&NK_NOTE_ASSET_ID.test(String(block.asset.id||'')));}
  function nkNoteAudioBlock(block){return Boolean(block&&block.type==='audio'&&NK_NOTE_ASSET_ID.test(String(block.assetId||'')));}
  function nkNoteAudioMime(value){const mime=String(value||'').split(';')[0].trim().toLowerCase();return NK_NOTE_AUDIO_MIME.test(mime)?mime:'audio/webm';}
  function nkNoteCleanAudio(block){
    return {type:'audio',assetId:String(block.assetId),durationMs:Math.max(0,Math.min(NK_NOTE_AUDIO_MAX_MS,Math.round(Number(block.durationMs)||0))),
      mime:nkNoteAudioMime(block.mime),caption:String(block.caption||'').replace(/\s+/g,' ').trim().slice(0,120),bytes:Math.max(0,Math.round(Number(block.bytes)||0))};
  }
  function nkNoteSanitizeBlocks(value){
    if(!Array.isArray(value))return [];
    const out=[];let media=0,texts=0,audio=0;
    for(const block of value.slice(0,40)){
      if(block&&block.type==='text'&&typeof block.text==='string'){
        const text=block.text.replace(/\r\n?/g,'\n').slice(0,2000);
        if(text.trim()&&texts<NK_NOTE_TEXT_LIMIT){out.push({type:'text',text});texts++;}
      }else if(nkNoteMediaBlock(block)&&media<NK_NOTE_MEDIA_LIMIT){
        const a=block.asset,mime=NK_NOTE_MIME.includes(a.mime)?a.mime:'image/jpeg';
        out.push({type:'image',source:block.source==='pdf'?'pdf':'image',label:String(block.label||'').slice(0,120),
          asset:{id:String(a.id),mime,w:Math.max(1,Math.round(Number(a.w)||1)),h:Math.max(1,Math.round(Number(a.h)||1)),bytes:Math.max(0,Math.round(Number(a.bytes)||0))}});
        media++;
      }else if(nkNoteAudioBlock(block)&&audio<NK_NOTE_AUDIO_LIMIT){out.push(nkNoteCleanAudio(block));audio++;}
    }
    return out;
  }
  // A note is ordered text and image parts. Older notes and older app versions only know `text`.
  function nkNoteBlocks(note){
    if(!note||note.deleted)return [];
    const text=typeof note.text==='string'?note.text:'';
    if(!Array.isArray(note.blocks))return text.trim()?[{type:'text',text}]:[];
    const blocks=nkNoteSanitizeBlocks(note.blocks);
    // An older app version edited the text after these parts were saved: keep its text, the images and voice clips.
    if(Number(note.blocksAt||0)<Number(note.updatedAt||0))return [...(text.trim()?[{type:'text',text}]:[]),...blocks.filter(block=>nkNoteMediaBlock(block)||nkNoteAudioBlock(block))];
    return blocks;
  }
  /* Voice clips sync in their own `noteVoice` kind, never inside `noteBlocks`. Older app
   * versions drop block types they do not know and would upload the shortened list again,
   * so `noteBlocks` carries exactly what they can keep, and each clip remembers its place. */
  function nkNoteVoiceClips(blocks){return (blocks||[]).flatMap((block,at)=>nkNoteAudioBlock(block)?[{...nkNoteCleanAudio(block),at}]:[]);}
  function nkNoteWithVoice(base,clips){
    const out=(base||[]).filter(block=>!nkNoteAudioBlock(block));
    (clips||[]).filter(nkNoteAudioBlock).map(clip=>({clip:nkNoteCleanAudio(clip),at:Math.max(0,Math.round(Number(clip.at)||0))})).sort((a,b)=>a.at-b.at)
      .slice(0,NK_NOTE_AUDIO_LIMIT).forEach(({clip,at})=>out.splice(Math.min(at,out.length),0,clip));
    return out;
  }
  // The notes as `noteBlocks` should see them: every part except voice clips.
  function nkNoteSyncNotes(notes){
    const out={};
    Object.entries(notes||{}).forEach(([qid,note])=>{out[qid]=note&&Array.isArray(note.blocks)&&note.blocks.some(nkNoteAudioBlock)?{...note,blocks:note.blocks.filter(block=>!nkNoteAudioBlock(block))}:note;});
    return out;
  }
  // [qid, payload, updatedAt] for each note with clips, or whose clips were synced before (so removals travel).
  function nkNoteVoiceEnvelopes(syncedBefore){
    return Object.entries(state.questionNotes||{}).flatMap(([qid,note])=>{
      if(!note||!Array.isArray(note.blocks))return [];
      const clips=nkNoteVoiceClips(note.blocks);
      if(!clips.length&&!(typeof syncedBefore==='function'&&syncedBefore(`noteVoice/${qid}`)))return [];
      return [[qid,{clips,deleted:Boolean(note.deleted)},Number(note.blocksAt||note.updatedAt||0)]];
    });
  }
  // Incoming `noteBlocks` never carry clips; put this device's clips back where they were.
  function nkNoteKeepVoice(prior,incoming){
    if((incoming||[]).some(nkNoteAudioBlock)||!Array.isArray(prior?.blocks))return incoming;
    return nkNoteWithVoice(incoming,nkNoteVoiceClips(nkNoteSanitizeBlocks(prior.blocks)));
  }
  function nkNoteApplyVoice(id,payload,updatedAt){
    const notes=state.questionNotes||{},prior=notes[String(id)];
    // Clips only join a note this device already has; the note itself arrives through `notes`.
    if(!prior||!payload||!Array.isArray(payload.clips))return false;
    const text=typeof prior.text==='string'?prior.text:'';
    const base=Array.isArray(prior.blocks)?nkNoteSanitizeBlocks(prior.blocks):(text.trim()?[{type:'text',text}]:[]);
    notes[String(id)]={...prior,blocks:nkNoteWithVoice(base,payload.clips),blocksAt:Math.max(Number(prior.blocksAt||0),Number(updatedAt||0))};
    return true;
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
    if(blocks.some(nkNoteMediaBlock)||blocks.some(nkNoteAudioBlock)||blocks.length>1||Array.isArray(previous?.blocks)){next.blocks=blocks;next.blocksAt=updatedAt;}
    notes[qid]=next;
    if(!saveState()){
      if(previous===undefined)delete notes[qid];else notes[qid]=previous;
      return false;
    }
    const kept=[...blocks.filter(nkNoteMediaBlock).map(block=>block.asset.id),...blocks.filter(nkNoteAudioBlock).map(block=>block.assetId)],keep=new Set(kept);
    const removed=[...before.filter(block=>nkNoteMediaBlock(block)&&!keep.has(block.asset.id)).map(block=>block.asset),
      ...before.filter(block=>nkNoteAudioBlock(block)&&!keep.has(block.assetId)).map(block=>({id:block.assetId,bytes:block.bytes}))];
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
  // Same folding as question search: accents, curly quotes and dashes match their plain forms.
  function nkNoteFold(value){return typeof nkQuestionSearchFold==='function'?nkQuestionSearchFold(value):String(value||'').toLowerCase().trim();}
  function nkNotesPage(){
    const entries=nkSavedQuestionNotes();
    return shell(`<div class="nk-app-v114 nk-notes-page">${nkAppPageHead('PERSONAL REVISION','My notes','Recall cues saved while reviewing questions.')}
      <div class="nk-notes-count">${fmtNum(entries.length)} saved note${entries.length===1?'':'s'}</div>
      ${entries.length?`<label class="nk-notes-search"><span aria-hidden="true">${navIcon('search',20)}</span><input type="search" value="${esc(nkNotesQuery)}" placeholder="Search notes or questions" aria-label="Search notes or questions" oninput="window.QB.nkFilterNotes(this.value)"></label>
      <div class="nk-notes-list">${entries.map(({id,note,q})=>{
        const subject=q?.subject||'Question unavailable',bank=q?.bank||'',topic=q?.chapter||q?.topic||'';
        const blocks=nkNoteBlocks(note),text=blocks.filter(block=>block.type==='text').map(block=>block.text).join('\n\n'),media=blocks.filter(nkNoteMediaBlock),voices=blocks.filter(nkNoteAudioBlock).length;
        const key=encodeURIComponent(id),search=esc(nkNoteFold(`${subject} ${bank} ${topic} ${q?.question||''} ${text}`));
        const strip=media.length&&typeof nkNoteMediaFrame==='function'?`<div class="nk-notes-item-media" aria-label="${media.length} image${media.length===1?'':'s'} in this note">${media.slice(0,4).map(block=>nkNoteMediaFrame(block,'thumb')).join('')}${media.length>4?`<span class="nk-notes-item-more">+${media.length-4}</span>`:''}</div>`:'';
        const voice=voices?`<div class="nk-notes-item-voice"><span aria-hidden="true">${NK_NOTE_ICON.mic}</span>${voices} voice clip${voices===1?'':'s'}</div>`:'';
        return `<article class="nk-notes-item" data-note-search="${search}"><div class="nk-notes-item-meta">${esc(subject)}${bank?` · ${esc(bank)}`:''}${topic?` · ${esc(topic)}`:''}</div><p class="nk-notes-item-question">${q?esc(q.question):'This question is not in the current banks.'}</p>${text?`<div class="nk-notes-item-text">${esc(text)}</div>`:''}${strip}${voice}${q?`<button type="button" onclick="window.QB.nkOpenNotedQuestion('${key}')">Practice question ${navIcon('chevron',16)}</button>`:''}</article>`;
      }).join('')}</div><p class="nk-notes-no-match" role="status" hidden>No notes match your search.</p>`:
      nkAppEmpty('book','No notes yet','After answering a question, add a recall cue below the answer. It will appear here.')}
    </div>`,'more');
  }

  function nkFilterNotes(value){
    nkNotesQuery=String(value||'');
    const term=nkNoteFold(nkNotesQuery),terms=term.split(/\s+/).filter(Boolean);
    let shown=0;
    document.querySelectorAll('.nk-notes-item').forEach(item=>{
      const haystack=item.dataset.noteSearch||'';
      item.hidden=Boolean(terms.length)&&!terms.every(word=>haystack.includes(word));
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
  const NK_NOTE_ICON={
    dots:'<svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor" aria-hidden="true"><circle cx="12" cy="5" r="1.9"/><circle cx="12" cy="12" r="1.9"/><circle cx="12" cy="19" r="1.9"/></svg>',
    back:'<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M19 12H5M11 18l-6-6 6-6"/></svg>',
    note:'<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M6 3h9l4 4v14H6z"/><path d="M14 3v5h5M9 12h7M9 16h5"/></svg>',
    chevron:'<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M9 6l6 6-6 6"/></svg>',
    plus:'<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" aria-hidden="true"><path d="M12 5v14M5 12h14"/></svg>',
    mic:'<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="9" y="3" width="6" height="11" rx="3"/><path d="M5.5 11a6.5 6.5 0 0 0 13 0M12 17.5V21"/></svg>'
  };
  function nkNoteCounts(blocks){
    const text=blocks.filter(block=>block.type==='text').length,media=blocks.filter(nkNoteMediaBlock);
    const pdf=media.filter(block=>block.source==='pdf').length,images=media.length-pdf,voice=blocks.filter(nkNoteAudioBlock).length;
    return [text&&`${text} text`,images&&`${images} image${images===1?'':'s'}`,pdf&&`${pdf} PDF page${pdf===1?'':'s'}`,voice&&`${voice} voice clip${voice===1?'':'s'}`].filter(Boolean).join(' · ');
  }
  function nkNoteBarHtml(qid){
    const blocks=nkNoteBlocks(state.questionNotes?.[qid]),first=blocks.find(block=>block.type==='text');
    const detail=blocks.length?(first?first.text.replace(/\s+/g,' ').slice(0,140):nkNoteCounts(blocks)):'Add text, images or PDF pages';
    const count=blocks.length?`<span class="nk-note-bar-count" aria-label="${esc(nkNoteCounts(blocks))}">${blocks.length}</span>`:'';
    return `<button type="button" class="nk-note-bar${blocks.length?' has-note':''}" aria-haspopup="dialog" aria-label="Open my notes"><span class="nk-note-bar-icon">${NK_NOTE_ICON.note}</span><span class="nk-note-bar-copy"><strong>My notes</strong><small>${esc(detail)}</small></span>${count}<span class="nk-note-bar-chevron">${NK_NOTE_ICON.chevron}</span></button>`;
  }
  function nkRefreshNoteBars(){
    document.querySelectorAll('.nk-question-note[data-qid]').forEach(section=>{
      section.innerHTML=nkNoteBarHtml(section.dataset.qid);
      section.querySelector('.nk-note-bar').addEventListener('click',()=>nkOpenNoteSheet(section.dataset.qid,section.dataset.title||''));
    });
  }

  let nkNoteSheetState=null;
  // Full-screen note: ordered text, image and PDF-page blocks. Every change saves immediately.
  function nkOpenNoteSheet(qid,title){
    if(nkNoteSheetState){if(nkNoteSheetState.qid===qid)return;nkNoteSheetState.close();}
    const opener=document.activeElement,root=document.documentElement,previousOverflow=root.style.overflow;
    const sheet=document.createElement('div');
    sheet.className='nk-note-page';sheet.setAttribute('role','dialog');sheet.setAttribute('aria-modal','true');sheet.setAttribute('aria-label','My notes');
    document.body.appendChild(sheet);root.style.overflow='hidden';
    let blocks=nkNoteBlocks(state.questionNotes?.[qid]).map(block=>({...block}));
    let editing=null,pending=0,progress='',menu=null,longPress=null,suppressClick=false,voice=null;
    const mediaReady=typeof nkNoteImportImage==='function',voiceReady=typeof nkNoteVoiceStart==='function';

    function label(block){return nkNoteAudioBlock(block)?(block.caption||'Voice clip'):block.label||(block.source==='pdf'?'PDF page':'Image');}
    function blockHtml(block,index,media){
      const dots=`<button type="button" class="nk-nb-dots" data-act="menu" data-i="${index}" aria-haspopup="menu" aria-label="Options for ${block.type==='text'?'note text':esc(label(block))}">${NK_NOTE_ICON.dots}</button>`;
      if(editing&&editing.index===index){
        return `<article class="nk-nb is-text is-editing" data-i="${index}"><label class="nk-nb-kind" for="nk-question-note-text">Note</label><textarea id="nk-question-note-text" maxlength="2000" rows="5" placeholder="Write the idea you want to recall later.">${esc(editing.text)}</textarea><div class="nk-nb-edit-actions"><small role="status">${esc(editing.status||'Up to 2,000 characters')}</small><div><button type="button" class="nk-note-cancel" data-act="cancel-edit">Cancel</button><button type="button" class="nk-note-save" data-act="save-edit">Save</button></div></div></article>`;
      }
      if(block.type==='text')return `<article class="nk-nb is-text" data-i="${index}"><div class="nk-nb-head"><span class="nk-nb-kind">Note</span>${dots}</div><div class="nk-nb-text nk-note-readonly">${esc(block.text)}</div></article>`;
      if(nkNoteAudioBlock(block))return `<article class="nk-nb is-audio" data-i="${index}"><div class="nk-nb-head"><span class="nk-nb-badge is-voice" aria-hidden="true">${NK_NOTE_ICON.mic}</span><span class="nk-nb-title">${esc(label(block))}</span>${dots}</div>${voiceReady?nkNoteVoicePlayer(block):''}</article>`;
      const frame=`<button type="button" class="nk-nb-open" data-act="open" data-m="${media}" aria-label="Open ${esc(label(block))} full screen">${typeof nkNoteMediaFrame==='function'?nkNoteMediaFrame(block,'preview'):''}</button>`;
      if(block.source==='pdf')return `<article class="nk-nb is-pdf" data-i="${index}"><div class="nk-nb-head"><span class="nk-nb-badge" aria-hidden="true">PDF</span><span class="nk-nb-title">${esc(label(block))}</span>${dots}</div>${frame}</article>`;
      return `<article class="nk-nb is-image" data-i="${index}">${frame}<div class="nk-nb-foot"><span class="nk-nb-caption">${esc(label(block))}</span>${dots}</div></article>`;
    }
    // The recorder sits below the blocks while it is open; only its clock changes between renders.
    function recorderHtml(){
      if(!voice)return '';
      const canRecord=nkNoteVoiceCanRecord(),limit=nkNoteClock(NK_NOTE_VOICE_MAX_MS);
      if(voice.phase==='recording'||voice.phase==='starting')return `<article class="nk-nb is-recorder is-recording" aria-label="Recording voice clip"><div class="nk-nr-row"><span class="nk-nr-dot" aria-hidden="true"></span><span class="nk-nr-label">${voice.phase==='starting'?'Starting microphone…':'Recording'}</span><span class="nk-nr-time" role="timer" aria-live="off">${nkNoteClock(voice.ms)} / ${limit}</span></div><div class="nk-nr-actions"><button type="button" class="nk-nr-cancel" data-act="voice-cancel">Discard</button><button type="button" class="nk-nr-stop" data-act="voice-stop"${voice.phase==='starting'?' disabled':''}>Stop and save</button></div></article>`;
      if(voice.phase==='saving')return '<article class="nk-nb is-recorder is-saving" aria-busy="true"><div class="nk-nr-row"><span class="nk-nr-label">Saving voice clip…</span></div><span class="nk-skel nk-skel-line"></span></article>';
      return `<article class="nk-nb is-recorder" aria-label="Add a voice clip"><div class="nk-nr-row"><span class="nk-nb-badge is-voice" aria-hidden="true">${NK_NOTE_ICON.mic}</span><span class="nk-nr-label">Voice clip</span><small class="nk-nr-hint">Up to ${limit} per clip</small><button type="button" class="nk-nr-close" data-act="voice-close" aria-label="Close recorder">✕</button></div>${voice.message?`<p class="nk-nr-message" role="alert">${esc(voice.message)}</p>`:''}<div class="nk-nr-actions"><button type="button" class="nk-nr-import" data-act="voice-import">Import audio</button><button type="button" class="nk-nr-record" data-act="voice-record"${canRecord?'':' disabled'}><span class="nk-nr-rec" aria-hidden="true"></span>Record</button></div></article>`;
    }
    function render(focusSelector){
      const scroller=sheet.querySelector('.nk-np-body'),top=scroller?scroller.scrollTop:0;
      let media=0;
      const items=blocks.map((block,index)=>blockHtml(block,index,nkNoteMediaBlock(block)?media++:-1)).join('');
      const skeletons=Array.from({length:pending},()=>'<article class="nk-nb is-skeleton" aria-hidden="true"><span class="nk-skel nk-skel-line"></span><span class="nk-skel nk-skel-box"></span></article>').join('');
      const empty=!blocks.length&&!pending?'<div class="nk-np-empty"><strong>No notes yet</strong><p>Add a key point, a GoodNotes page, a screenshot or PDF pages for this question.</p></div>':'';
      const mediaCount=blocks.filter(nkNoteMediaBlock).length,textCount=blocks.filter(block=>block.type==='text').length,full=mediaCount+pending>=NK_NOTE_MEDIA_LIMIT;
      const voiceFull=blocks.filter(nkNoteAudioBlock).length>=NK_NOTE_AUDIO_LIMIT||Boolean(voice);
      sheet.innerHTML=`<header class="nk-np-head"><button type="button" class="nk-np-back" data-act="close" aria-label="Close notes">${NK_NOTE_ICON.back}</button><h2>Notes${title?` <span>· ${esc(title)}</span>`:''}</h2></header><div class="nk-np-body"><div class="nk-np-blocks">${items}${skeletons}${voice?recorderHtml():empty}</div><p class="nk-np-status" role="status" aria-live="polite">${esc(progress)}</p></div><div class="nk-np-add"><div class="nk-np-add-menu" role="menu" aria-label="Add block" hidden><button type="button" role="menuitem" data-act="add-text"${textCount>=NK_NOTE_TEXT_LIMIT?' disabled':''}>Text</button>${mediaReady?`<button type="button" role="menuitem" data-act="add-image"${full?' disabled':''}>Image</button><button type="button" role="menuitem" data-act="add-pdf"${full?' disabled':''}>PDF pages</button>`:''}${voiceReady?`<button type="button" role="menuitem" data-act="add-voice"${voiceFull?' disabled':''}>Voice</button>`:''}</div><button type="button" class="nk-np-add-btn" data-act="add" aria-haspopup="menu" aria-expanded="false">${NK_NOTE_ICON.plus}<span>Add block</span></button>${mediaReady?'<input type="file" class="nk-note-file nk-note-file-image" accept="image/*" multiple tabindex="-1" aria-hidden="true"><input type="file" class="nk-note-file nk-note-file-pdf" accept="application/pdf,.pdf" tabindex="-1" aria-hidden="true">':''}${voiceReady?'<input type="file" class="nk-note-file nk-note-file-audio" accept="audio/*" tabindex="-1" aria-hidden="true">':''}</div>`;
      const body=sheet.querySelector('.nk-np-body');body.scrollTop=top;
      sheet.querySelectorAll('input[type="file"]').forEach(input=>input.addEventListener('change',()=>{const files=[...(input.files||[])];input.value='';importFiles(files);}));
      const area=sheet.querySelector('textarea');
      if(area){area.addEventListener('input',()=>{editing.text=area.value;nkNoteDrafts.set(qid,area.value);});}
      if(typeof nkNoteHydrate==='function')nkNoteHydrate(sheet);
      if(focusSelector)sheet.querySelector(focusSelector)?.focus({preventScroll:false});
    }
    function commit(next){
      const saved=next.filter(block=>block.type!=='text'||block.text.trim());
      if(!nkSaveQuestionNoteBlocks(qid,saved))return false;
      blocks=next;nkRefreshNoteBars();return true;
    }
    function saveEdit(){
      if(!editing)return true;
      const text=editing.text.replace(/\r\n?/g,'\n').trim();
      if(!text){editing.status='Write a note before saving.';render('textarea');return false;}
      const next=blocks.map((block,index)=>index===editing.index?{type:'text',text}:block);
      if(!commit(next)){editing.status='Save failed. Your text is still here.';render('textarea');return false;}
      editing=null;nkNoteDrafts.delete(qid);return true;
    }
    function cancelEdit(){
      if(editing?.isNew)blocks.splice(editing.index,1);
      editing=null;nkNoteDrafts.delete(qid);
    }
    function startText(index){
      if(editing&&!saveEdit())return;
      if(index==null){blocks.push({type:'text',text:''});index=blocks.length-1;editing={index,text:'',isNew:true};}
      else editing={index,text:blocks[index].text,isNew:false};
      render('textarea');sheet.querySelector('.nk-nb.is-editing')?.scrollIntoView({block:'center',behavior:'instant'});
    }
    function closeMenu(){if(menu){menu.remove();menu=null;}}
    function openMenu(index,x,y){
      closeMenu();
      const block=blocks[index];if(!block)return;
      menu=document.createElement('div');menu.className='nk-nb-menu';menu.setAttribute('role','menu');
      const first=block.type==='text'?'<button type="button" role="menuitem" data-act="edit">Edit</button>':nkNoteAudioBlock(block)?'<button type="button" role="menuitem" data-act="rename">Rename caption</button>':'<button type="button" role="menuitem" data-act="view">View full screen</button>';
      menu.innerHTML=`${first}<button type="button" role="menuitem" data-act="up"${index===0?' disabled':''}>Move up</button><button type="button" role="menuitem" data-act="down"${index===blocks.length-1?' disabled':''}>Move down</button><button type="button" role="menuitem" data-act="delete" class="is-danger">Delete</button>`;
      sheet.appendChild(menu);
      const rect=menu.getBoundingClientRect(),left=Math.max(8,Math.min(window.innerWidth-rect.width-8,x-rect.width)),below=y+rect.height+8<=window.innerHeight;
      menu.style.left=`${left}px`;menu.style.top=`${below?y:Math.max(8,y-rect.height)}px`;
      menu.addEventListener('click',event=>{
        const item=event.target.closest('[data-act]');if(!item||item.disabled)return;
        const act=item.dataset.act;closeMenu();
        if(act==='edit')startText(index);
        else if(act==='rename'){
          const caption=prompt('Caption for this voice clip',block.caption||'');
          if(caption==null)return;
          if(editing&&!saveEdit())return;
          const next=blocks.map((item,i)=>i===index?{...item,caption:caption.replace(/\s+/g,' ').trim().slice(0,120)}:item);
          if(commit(next))render(`.nk-nb[data-i="${index}"] .nk-nb-dots`);else showToast('Could not save the note. Please try again.','bad');
        }
        else if(act==='view'){const media=blocks.filter(nkNoteMediaBlock);if(typeof nkNoteOpenViewer==='function')nkNoteOpenViewer(blocks,media.indexOf(block));}
        else if(act==='up'||act==='down'){
          if(editing&&!saveEdit())return;
          const target=act==='up'?index-1:index+1,next=[...blocks];[next[index],next[target]]=[next[target],next[index]];
          if(commit(next))render(`.nk-nb[data-i="${target}"] .nk-nb-dots`);else showToast('Could not save the note. Please try again.','bad');
        }else if(act==='delete'){
          if((nkNoteMediaBlock(block)||nkNoteAudioBlock(block))&&!confirm(`Delete “${label(block)}” from this note?`))return;
          if(editing&&editing.index!==index&&!saveEdit())return;
          if(editing?.index===index){cancelEdit();if(block.type==='text'&&!block.text.trim()){render();return;}}
          const next=blocks.filter((_,i)=>i!==index);
          if(commit(next))render();else showToast('Could not delete. Please try again.','bad');
        }
      });
      menu.querySelector('button:not([disabled])')?.focus({preventScroll:true});
    }
    async function importFiles(files){
      if(!files.length||!mediaReady)return;
      if(editing&&!saveEdit())return;
      for(const file of files){
        if(voiceReady&&nkNoteIsAudioFile(file)){
          if(blocks.filter(nkNoteAudioBlock).length>=NK_NOTE_AUDIO_LIMIT){showToast(`A note holds up to ${NK_NOTE_AUDIO_LIMIT} voice clips.`,'bad');continue;}
          pending=1;progress='Adding voice clip…';render();
          try{const clip=await nkNoteImportAudio(file);if(!commit([...blocks,clip]))showToast('Could not save the note. Please try again.','bad');else voice=null;}
          catch(error){if(voice)voice.message=String(error?.message||error);else showToast(String(error?.message||error||'Could not add this file.'),'bad');}
          pending=0;progress='';
          if(!sheet.isConnected)return;
          render();continue;
        }
        const remaining=NK_NOTE_MEDIA_LIMIT-blocks.filter(nkNoteMediaBlock).length;
        if(remaining<=0){showToast(`A note holds up to ${NK_NOTE_MEDIA_LIMIT} images or pages.`,'bad');break;}
        const pdf=/pdf$/i.test(file.type||'')||/\.pdf$/i.test(file.name||'');
        pending=1;progress=pdf?'Opening PDF…':'Adding image…';render();
        try{
          const added=pdf?await nkNoteImportPdf(file,remaining,text=>{progress=text;const status=sheet.querySelector('.nk-np-status');if(status)status.textContent=text;}):[await nkNoteImportImage(file)];
          if(added.length&&!commit([...blocks,...added]))showToast('Could not save the note. Please try again.','bad');
        }catch(error){showToast(String(error?.message||error||'Could not add this file.'),'bad');}
        pending=0;progress='';
        if(!sheet.isConnected)return;
        render();
      }
      sheet.querySelector('.nk-nb:last-of-type')?.scrollIntoView({block:'nearest',behavior:'smooth'});
    }
    function openRecorder(){
      if(editing&&!saveEdit())return;
      if(blocks.filter(nkNoteAudioBlock).length>=NK_NOTE_AUDIO_LIMIT){showToast(`A note holds up to ${NK_NOTE_AUDIO_LIMIT} voice clips.`,'bad');return;}
      voice={phase:'idle',ms:0,message:nkNoteVoiceCanRecord()?'':nkNoteVoiceError(Object.assign(new Error('This browser cannot record audio. You can import an audio file instead.'),{name:'NotSupportedError'}))};
      render('.nk-nr-record:not([disabled]),.nk-nr-import');
      sheet.querySelector('.nk-nb.is-recorder')?.scrollIntoView({block:'nearest',behavior:'smooth'});
    }
    async function startRecording(){
      if(!voice||voice.phase!=='idle')return;
      voice={phase:'starting',ms:0,message:''};render();
      const session=voice;
      try{
        session.ctrl=await nkNoteVoiceStart({
          onTick:ms=>{session.ms=ms;const clock=sheet.querySelector('.nk-nr-time');if(clock&&voice===session)clock.textContent=`${nkNoteClock(ms)} / ${nkNoteClock(NK_NOTE_VOICE_MAX_MS)}`;},
          onAutoStop:()=>{if(voice===session)stopRecording(true);}
        });
        if(voice!==session){session.ctrl.cancel();return;}
        session.phase='recording';
        if(sheet.isConnected)render('.nk-nr-stop');
      }catch(error){
        if(voice!==session)return;
        voice={phase:'idle',ms:0,message:nkNoteVoiceError(error)};
        if(sheet.isConnected)render('.nk-nr-import');
      }
    }
    async function stopRecording(auto){
      const session=voice;if(!session||session.phase!=='recording'||!session.ctrl)return;
      session.phase='saving';if(sheet.isConnected)render();
      try{
        const clip=await session.ctrl.stop();
        if(clip&&!commit([...blocks,clip]))throw new Error('Could not save the note. Please try again.');
        if(voice===session)voice=null;
        if(auto)showToast('Saved: voice clips stop at 3 minutes.','good');
      }catch(error){
        if(voice===session)voice={phase:'idle',ms:0,message:String(error?.message||error||'The recording could not be saved.')};
      }
      if(sheet.isConnected){render();sheet.querySelector('.nk-nb.is-audio:last-of-type')?.scrollIntoView({block:'nearest',behavior:'smooth'});}
    }
    function closeRecorder(){
      const session=voice;voice=null;
      if(session?.phase==='recording'||session?.phase==='starting')session.ctrl?.cancel();
    }
    function toggleAdd(force){
      const list=sheet.querySelector('.nk-np-add-menu'),button=sheet.querySelector('.nk-np-add-btn');if(!list)return;
      const open=force==null?list.hidden:force;list.hidden=!open;button.setAttribute('aria-expanded',String(open));
      if(open)list.querySelector('button:not([disabled])')?.focus({preventScroll:true});
    }
    function close(){
      if(!sheet.isConnected)return;
      if(editing&&editing.text.trim())saveEdit();else cancelEdit();
      // Leaving while recording keeps the clip, as leaving keeps typed text.
      if(voice?.phase==='recording')stopRecording(false);else if(voice?.phase!=='saving')closeRecorder();
      closeMenu();clearTimeout(longPress?.timer);
      document.removeEventListener('keydown',onKey);document.removeEventListener('pointerdown',onOutside,true);
      sheet.remove();root.style.overflow=previousOverflow;nkNoteSheetState=null;
      nkRefreshNoteBars();
      (document.querySelector(`.nk-question-note[data-qid="${CSS.escape(qid)}"] .nk-note-bar`)||opener)?.focus?.({preventScroll:true});
    }
    function onKey(event){
      if(event.key!=='Escape')return;
      if(menu){closeMenu();return;}
      const list=sheet.querySelector('.nk-np-add-menu');if(list&&!list.hidden){toggleAdd(false);return;}
      if(voice){if(voice.phase==='recording')stopRecording(false);else if(voice.phase==='idle'){closeRecorder();render();}return;}
      // Escape keeps typed text, as closing the sheet does.
      if(editing){if(!editing.text.trim()){cancelEdit();render();}else if(saveEdit())render();return;}
      close();
    }
    function onOutside(event){
      if(menu&&!menu.contains(event.target))closeMenu();
      const add=sheet.querySelector('.nk-np-add');if(add&&!add.contains(event.target))toggleAdd(false);
    }
    document.addEventListener('keydown',onKey);document.addEventListener('pointerdown',onOutside,true);
    sheet.addEventListener('click',event=>{
      if(suppressClick){suppressClick=false;event.preventDefault();return;}
      const target=event.target.closest('[data-act]');if(!target||target.disabled)return;
      const act=target.dataset.act;
      if(act==='close')close();
      else if(act==='menu'){const r=target.getBoundingClientRect();openMenu(Number(target.dataset.i),r.right,r.bottom+4);}
      else if(act==='open'){if(typeof nkNoteOpenViewer==='function')nkNoteOpenViewer(blocks,Number(target.dataset.m),target.querySelector('img'));}
      else if(act==='save-edit'){if(saveEdit())render();}
      else if(act==='cancel-edit'){cancelEdit();render();}
      else if(act==='add')toggleAdd();
      else if(act==='add-text'){toggleAdd(false);startText(null);}
      else if(act==='add-image'){toggleAdd(false);sheet.querySelector('.nk-note-file-image')?.click();}
      else if(act==='add-pdf'){toggleAdd(false);sheet.querySelector('.nk-note-file-pdf')?.click();}
      else if(act==='add-voice'){toggleAdd(false);openRecorder();}
      else if(act==='voice-record')startRecording();
      else if(act==='voice-stop')stopRecording(false);
      else if(act==='voice-cancel'||act==='voice-close'){closeRecorder();render();}
      else if(act==='voice-import')sheet.querySelector('.nk-note-file-audio')?.click();
    });
    // Long-press any block (or right-click) for the same menu as its ⋮ button.
    sheet.addEventListener('pointerdown',event=>{
      const block=event.target.closest('.nk-nb:not(.is-editing):not(.is-skeleton):not(.is-recorder)');
      if(!block||event.target.closest('.nk-nb-dots,.nk-nv-player')||(event.pointerType==='mouse'&&event.button!==0))return;
      const index=Number(block.dataset.i),x=event.clientX,y=event.clientY;
      longPress={x,y,timer:setTimeout(()=>{longPress=null;suppressClick=true;navigator.vibrate?.(10);openMenu(index,x+12,y+8);},480)};
    });
    const cancelPress=event=>{if(!longPress)return;if(event.type==='pointermove'&&Math.hypot(event.clientX-longPress.x,event.clientY-longPress.y)<10)return;clearTimeout(longPress.timer);longPress=null;};
    ['pointermove','pointerup','pointercancel'].forEach(type=>sheet.addEventListener(type,cancelPress));
    sheet.addEventListener('scroll',cancelPress,true);
    sheet.addEventListener('contextmenu',event=>{const block=event.target.closest('.nk-nb:not(.is-editing):not(.is-skeleton):not(.is-recorder)');if(!block)return;event.preventDefault();clearTimeout(longPress?.timer);longPress=null;openMenu(Number(block.dataset.i),event.clientX+12,event.clientY+8);});
    sheet.addEventListener('paste',event=>{
      const files=[...(event.clipboardData?.files||[])].filter(file=>/^image\//.test(file.type||''));
      if(!files.length)return;event.preventDefault();importFiles(files);
    });
    sheet.addEventListener('dragover',event=>{if([...(event.dataTransfer?.types||[])].includes('Files'))event.preventDefault();});
    sheet.addEventListener('drop',event=>{const files=[...(event.dataTransfer?.files||[])];if(!files.length)return;event.preventDefault();importFiles(files);});

    nkNoteSheetState={qid,close};
    render();
    if(!blocks.length)toggleAdd(true);else sheet.querySelector('.nk-np-back')?.focus({preventScroll:true});
  }

  function nkMountQuestionNote(){
    const account=String(typeof nkAuth!=="undefined"&&nkAuth?.uid||"local");
    if(account!==nkNotesAccount){nkNotesQuery="";nkNotesAccount=account;}
    const owner=account+":"+String(state.activeSession?.id||"");
    if(owner!==nkNoteDraftOwner){nkNoteDrafts.clear();nkNoteDraftOwner=owner;}
    const page=route.page;
    if(page==='notes'){nkNoteSheetState?.close();nkFilterNotes(nkNotesQuery);if(typeof nkNoteHydrate==='function')nkNoteHydrate(document.querySelector('.nk-notes-page'));return;}
    const session=state.activeSession,qid=String(session?.questionIds?.[session?.index]||'');
    if(nkNoteSheetState&&(nkNoteSheetState.qid!==qid||(page!=='practice'&&page!=='review-test')))nkNoteSheetState.close();
    if(page!=='practice'&&page!=='review-test')return;
    if(!BY_ID[qid]||(page==='practice'&&!session?.submitted?.[qid]))return;
    const card=document.querySelector('.question-card');if(!card)return;
    const section=document.createElement('section');
    section.className='nk-question-note';section.dataset.qid=qid;section.dataset.title=`Question ${Number(session.index||0)+1}`;
    const source=card.querySelector('.nk-source-section');
    const feedback=card.querySelector('.feedback,.nk-practice-response');
    if(source)source.insertAdjacentElement('beforebegin',section);
    else if(feedback)feedback.insertAdjacentElement('beforebegin',section);
    else card.appendChild(section);
    section.innerHTML=nkNoteBarHtml(qid);
    section.querySelector('.nk-note-bar').addEventListener('click',()=>nkOpenNoteSheet(qid,section.dataset.title));
  }
  /* NK_QUESTION_NOTES_V1_END */
