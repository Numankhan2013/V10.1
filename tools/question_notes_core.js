  /* NK_QUESTION_NOTES_V1_START */
  function nkQuestionNote(id){
    const record=state.questionNotes?.[String(id)];
    return record&&!record.deleted&&typeof record.text==='string'&&record.text.trim()?record:null;
  }

  function nkSaveQuestionNote(id,value){
    const qid=String(id),text=String(value||'').replace(/\r\n?/g,'\n').trim();
    if(!BY_ID[qid]||text.length>2000)return false;
    const notes=state.questionNotes||(state.questionNotes={}),previous=notes[qid];
    if((previous&&!previous.deleted?previous.text:'')===text)return true;
    notes[qid]={text,updatedAt:Math.max(Date.now(),Number(previous?.updatedAt||0)+1),deleted:!text};
    if(!saveState()){
      if(previous===undefined)delete notes[qid];else notes[qid]=previous;
      return false;
    }
    showToast(text?'Note saved.':'Note removed.','good');
    return true;
  }

  function nkSavedQuestionNotes(){
    const questions=typeof nkAllBankQuestions==='function'?nkAllBankQuestions():nkAllStudyQuestions();
    const byId=new Map(questions.map(q=>[String(q.id),q]));
    return Object.entries(state.questionNotes||{}).flatMap(([id,note])=>
      note&&!note.deleted&&typeof note.text==='string'&&note.text.trim()?
        [{id,note,q:byId.get(id)||null}]:[]
    ).sort((a,b)=>Number(b.note.updatedAt||0)-Number(a.note.updatedAt||0));
  }

  function nkNotesPage(){
    const entries=nkSavedQuestionNotes();
    return shell(`<div class="nk-app-v114 nk-notes-page">${nkAppPageHead('PERSONAL REVISION','My notes','Recall cues saved while reviewing questions.')}
      <div class="nk-notes-count">${fmtNum(entries.length)} saved note${entries.length===1?'':'s'}</div>
      ${entries.length?`<label class="nk-notes-search"><span aria-hidden="true">⌕</span><input type="search" placeholder="Search notes or questions" aria-label="Search notes or questions" oninput="window.QB.nkFilterNotes(this.value)"></label>
      <div class="nk-notes-list">${entries.map(({id,note,q})=>{
        const subject=q?.subject||'Question unavailable',bank=q?.bank||'',topic=q?.chapter||q?.topic||'';
        const key=encodeURIComponent(id),search=esc(`${subject} ${bank} ${topic} ${q?.question||''} ${note.text}`.toLowerCase());
        return `<article class="nk-notes-item" data-note-search="${search}"><div class="nk-notes-item-meta">${esc(subject)}${bank?` · ${esc(bank)}`:''}${topic?` · ${esc(topic)}`:''}</div><p class="nk-notes-item-question">${q?esc(q.question):'This question is not in the current banks.'}</p><div class="nk-notes-item-text">${esc(note.text)}</div>${q?`<button type="button" onclick="window.QB.nkOpenNotedQuestion('${key}')">Practice question <span aria-hidden="true">›</span></button>`:''}</article>`;
      }).join('')}</div><p class="nk-notes-no-match" hidden>No notes match your search.</p>`:
      nkAppEmpty('book','No notes yet','After answering a question, add a recall cue below the answer. It will appear here.')}
    </div>`,'more');
  }

  function nkFilterNotes(value){
    const term=String(value||'').trim().toLowerCase();
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
    practiceOne(id);
  }

  function nkMountQuestionNote(){
    const page=route.page;
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

    function showReadOnly(focus=false){
      const note=nkQuestionNote(qid);
      if(!note){
        section.innerHTML='<div class="nk-question-note-head"><div><strong>My note</strong><small>Add a point to remember</small></div><button type="button" class="nk-note-add">Add note</button></div>';
        section.querySelector('.nk-note-add').addEventListener('click',()=>showEditor(''));
        if(focus)section.querySelector('.nk-note-add').focus();
        return;
      }
      section.innerHTML=`<div class="nk-question-note-head"><div><strong>My note</strong><small>Saved for this question</small></div><div class="nk-note-tools"><button type="button" class="nk-note-edit" aria-label="Edit note">Edit</button><button type="button" class="nk-note-delete" aria-label="Delete note">Delete</button></div></div><div class="nk-note-readonly">${esc(note.text)}</div>`;
      section.querySelector('.nk-note-edit').addEventListener('click',()=>showEditor(note.text));
      section.querySelector('.nk-note-delete').addEventListener('click',()=>{
        if(nkSaveQuestionNote(qid,''))showReadOnly(true);
        else showToast('Could not delete the note. Please try again.','bad');
      });
      if(focus)section.querySelector('.nk-note-edit').focus();
    }

    function showEditor(text){
      section.innerHTML=`<div class="nk-question-note-head"><div><strong>My note</strong><small>${nkQuestionNote(qid)?'Edit your recall cue':'Add a point to remember'}</small></div></div><div class="nk-question-note-body"><label for="nk-question-note-text">Your own words</label><textarea id="nk-question-note-text" maxlength="2000" rows="4" placeholder="Write the idea you want to recall later.">${esc(text)}</textarea><div class="nk-question-note-actions"><small role="status">Up to 2,000 characters</small><div><button type="button" class="nk-note-cancel">Cancel</button><button type="button" class="nk-note-save">Save note</button></div></div></div>`;
      const input=section.querySelector('textarea'),status=section.querySelector('[role="status"]');
      section.querySelector('.nk-note-cancel').addEventListener('click',()=>showReadOnly(true));
      section.querySelector('.nk-note-save').addEventListener('click',()=>{
        if(!input.value.trim()){status.textContent='Write a note before saving.';return;}
        if(!nkSaveQuestionNote(qid,input.value)){
          status.textContent='Save failed. Your text is still here.';
          return;
        }
        showReadOnly(true);
      });
      input.focus();
    }
    showReadOnly();
  }
  /* NK_QUESTION_NOTES_V1_END */
