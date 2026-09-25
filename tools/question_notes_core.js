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

  function nkMountQuestionNote(){
    const page=route.page;
    if(page!=='practice'&&page!=='review-test')return;
    const session=state.activeSession,qid=String(session?.questionIds?.[session.index]||'');
    if(!BY_ID[qid]||(page==='practice'&&!session?.submitted?.[qid]))return;
    const card=document.querySelector('.question-card');if(!card)return;
    const note=nkQuestionNote(qid),section=document.createElement('section');
    section.className='nk-question-note';
    section.innerHTML=`<details ${note?'open':''}><summary><span><strong>My note</strong><small>${note?'Saved for this question':'Add a point to remember'}</small></span><span aria-hidden="true">⌄</span></summary><div class="nk-question-note-body"><label for="nk-question-note-text">Your own words</label><textarea id="nk-question-note-text" maxlength="2000" rows="4" placeholder="Write the idea you want to recall later.">${note?esc(note.text):''}</textarea><div class="nk-question-note-actions"><small role="status">${note?'Saved on this device':'Up to 2,000 characters'}</small><button type="button">Save note</button></div></div></details>`;
    const source=card.querySelector('.nk-source-section');
    const feedback=card.querySelector('.feedback,.nk-practice-response');
    if(source)source.insertAdjacentElement('beforebegin',section);
    else if(feedback)feedback.insertAdjacentElement('beforebegin',section);
    else card.appendChild(section);
    const input=section.querySelector('textarea'),button=section.querySelector('button'),status=section.querySelector('[role="status"]');
    button.addEventListener('click',()=>{
      const value=input.value;
      if(!nkSaveQuestionNote(qid,value)){
        status.textContent='Save failed. Your text is still here.';
        return;
      }
      const saved=nkQuestionNote(qid);
      section.querySelector('summary small').textContent=saved?'Saved for this question':'Add a point to remember';
      status.textContent=saved?'Saved on this device':'Note removed';
    });
  }
  /* NK_QUESTION_NOTES_V1_END */
