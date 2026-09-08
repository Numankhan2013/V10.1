/* NK_CUSTOM_STUDY_MODULES_V1_START */
  let studyModuleDraft=null;

  function nkStudyModuleList(){
    return Array.isArray(state.studyModules)?state.studyModules:[];
  }

  function nkFindStudyModule(id){
    return nkStudyModuleList().find(module=>String(module.id)===String(id))||null;
  }

  function nkModuleTopicKey(subject,topicId){
    return `${String(subject)}::${String(topicId)}`;
  }

  function nkModuleSubjectRecord(name){
    return SUBJECTS.find(record=>String(record.subject)===String(name))||null;
  }

  function nkModuleTopics(record){
    return Array.isArray(record?.topics)?record.topics:(Array.isArray(record?.chapters)?record.chapters:[]);
  }

  function nkModuleValidQuestionIds(module){
    return [...new Set((Array.isArray(module?.questionIds)?module.questionIds:[]).map(String))].filter(id=>BY_ID[id]);
  }

  function nkModuleCompletedSet(module){
    const valid=new Set(nkModuleValidQuestionIds(module));
    return new Set((Array.isArray(module?.completedQuestionIds)?module.completedQuestionIds:[]).map(String).filter(id=>valid.has(id)));
  }

  function nkModuleProgress(module){
    const ids=nkModuleValidQuestionIds(module),completed=nkModuleCompletedSet(module);
    return {total:ids.length,completed:completed.size,remaining:Math.max(0,ids.length-completed.size),missing:Math.max(0,(module?.questionIds?.length||0)-ids.length)};
  }

  function nkNormalizeStudyModule(module){
    if(!module||typeof module!=='object')return null;
    const questionIds=[...new Set((Array.isArray(module.questionIds)?module.questionIds:[]).map(String))];
    if(!module.id||!questionIds.length)return null;
    const valid=new Set(questionIds);
    const completedQuestionIds=[...new Set((Array.isArray(module.completedQuestionIds)?module.completedQuestionIds:[]).map(String))].filter(id=>valid.has(id));
    return {
      id:String(module.id),name:String(module.name||'Study module').trim()||'Study module',
      subjectIds:[...new Set((Array.isArray(module.subjectIds)?module.subjectIds:[]).map(String))],
      topicIds:[...new Set((Array.isArray(module.topicIds)?module.topicIds:[]).map(String))],
      questionPoolType:['unattempted','wrong','bookmarked','mixed'].includes(module.questionPoolType)?module.questionPoolType:'mixed',
      questionIds,totalQuestions:Number(module.totalQuestions||questionIds.length),completedQuestionIds,
      currentPosition:Math.max(0,Number(module.currentPosition||0)),answers:{...(module.answers||{})},
      submitted:{...(module.submitted||{})},questionTimes:{...(module.questionTimes||{})},
      createdAt:Number(module.createdAt||Date.now()),lastOpenedAt:Number(module.lastOpenedAt||module.createdAt||Date.now()),
      completedAt:module.completedAt?Number(module.completedAt):null,isCompleted:Boolean(module.isCompleted),
      resultTestId:module.resultTestId?String(module.resultTestId):null
    };
  }

  function nkNormalizeStudyModules(){
    const raw=Array.isArray(state.studyModules)?state.studyModules:[];
    state.studyModules=raw.map(nkNormalizeStudyModule).filter(Boolean).slice(-100);
  }

  function nkSyncModuleFromSession(){
    const s=state.activeSession;
    if(!s?.studyModuleId)return;
    const module=nkFindStudyModule(s.studyModuleId);if(!module)return;
    const moduleIds=new Set((module.questionIds||[]).map(String));
    module.answers={...(s.answers||{})};
    module.submitted={...(s.submitted||{})};
    module.questionTimes={...(s.questionTimes||{})};
    module.currentPosition=Math.max(0,Number(s.index||0));
    module.completedQuestionIds=[...moduleIds].filter(id=>Boolean(module.submitted[id]));
    module.lastOpenedAt=Date.now();
  }

  function nkStudyModulePoolLabel(type){
    return {unattempted:'Unattempted',wrong:'Wrong',bookmarked:'Bookmarked',mixed:'Wrong + Unattempted'}[type]||'Mixed';
  }

  function nkStudyModuleTopicSummary(module){
    const subjects=(module.subjectIds||[]).filter(name=>nkModuleSubjectRecord(name));
    const labels=[];
    (module.topicIds||[]).forEach(key=>{
      const split=String(key).indexOf('::');if(split<0)return;
      const subject=String(key).slice(0,split),id=String(key).slice(split+2),record=nkModuleSubjectRecord(subject);
      const topic=nkModuleTopics(record).find(item=>String(item.id)===id);if(topic)labels.push(topic.title);
    });
    const subjectCopy=subjects.join(' + ')||'Selected subjects';
    const topicCopy=labels.length<=2?labels.join(' + '):`${labels.slice(0,2).join(' + ')} +${labels.length-2}`;
    return topicCopy?`${subjectCopy} · ${topicCopy}`:subjectCopy;
  }

  function nkStudyModuleAutoName(draft=studyModuleDraft){
    if(!draft)return 'Focused Revision';
    const labels=[];
    (draft.topicIds||[]).forEach(key=>{
      const split=String(key).indexOf('::');if(split<0)return;
      const subject=String(key).slice(0,split),id=String(key).slice(split+2),record=nkModuleSubjectRecord(subject);
      const topic=nkModuleTopics(record).find(item=>String(item.id)===id);if(topic)labels.push(topic.title);
    });
    if(labels.length===1)return `${labels[0]} Revision`;
    if(labels.length===2)return `${labels[0]} + ${labels[1]}`;
    if((draft.subjectIds||[]).length===1)return `${draft.subjectIds[0]} Mixed Review`;
    return 'Mixed Subjects Review';
  }

  function nkHashSeed(value){
    let hash=2166136261;for(const char of String(value)){hash^=char.charCodeAt(0);hash=Math.imul(hash,16777619);}return hash>>>0;
  }

  function nkSeededShuffle(values,seed){
    const out=[...values];let x=nkHashSeed(seed)||1;
    const random=()=>{x^=x<<13;x^=x>>>17;x^=x<<5;return (x>>>0)/4294967296;};
    for(let i=out.length-1;i>0;i--){const j=Math.floor(random()*(i+1));[out[i],out[j]]=[out[j],out[i]];}return out;
  }

  function nkQuestionsForModuleDraft(draft=studyModuleDraft){
    if(!draft)return [];
    const subjects=new Set(draft.subjectIds||[]),topics=new Set(draft.topicIds||[]);
    const scoped=[];
    SUBJECTS.forEach(record=>{
      if(!subjects.has(record.subject))return;
      (record.questions||[]).forEach(q=>{if(topics.has(nkModuleTopicKey(record.subject,q.chapterId)))scoped.push({...q,subject:q.subject||record.subject});});
    });
    const unique=[...new Map(scoped.map(q=>[String(q.id),q])).values()];
    return unique.filter(q=>{
      const attempts=qAttempts(q.id),wrong=attempts.some(attempt=>attempt&&!attempt.correct),bookmarked=Boolean(state.bookmarks?.[q.id]),unattempted=!attempts.length;
      if(draft.questionPoolType==='wrong')return wrong;
      if(draft.questionPoolType==='bookmarked')return bookmarked;
      if(draft.questionPoolType==='unattempted')return unattempted;
      return wrong||unattempted||bookmarked;
    });
  }

  function nkSelectModuleQuestionIds(draft=studyModuleDraft,seed='module'){
    const eligible=nkQuestionsForModuleDraft(draft),limit=Math.min(Math.max(1,Number(draft?.questionCount||20)),eligible.length);
    if(!limit)return [];
    if(draft.questionPoolType!=='mixed')return nkSeededShuffle(eligible.map(q=>String(q.id)),`${seed}:${draft.questionPoolType}`).slice(0,limit);
    const groups={wrong:[],unattempted:[],bookmarked:[]};
    eligible.forEach(q=>{
      const attempts=qAttempts(q.id);
      if(attempts.some(attempt=>attempt&&!attempt.correct))groups.wrong.push(String(q.id));
      if(!attempts.length)groups.unattempted.push(String(q.id));
      if(state.bookmarks?.[q.id])groups.bookmarked.push(String(q.id));
    });
    Object.keys(groups).forEach(key=>{groups[key]=nkSeededShuffle(groups[key],`${seed}:${key}`);});
    const selected=[],seen=new Set(),order=['wrong','wrong','unattempted','wrong','unattempted','bookmarked'];
    let cursor=0,progress=true;
    while(selected.length<limit&&progress){progress=false;for(const key of order){while(groups[key].length&&seen.has(groups[key][0]))groups[key].shift();if(groups[key].length){const id=groups[key].shift();seen.add(id);selected.push(id);progress=true;if(selected.length===limit)break;}}cursor++;if(cursor>eligible.length+2)break;}
    if(selected.length<limit){nkSeededShuffle(eligible.map(q=>String(q.id)),`${seed}:fill`).forEach(id=>{if(selected.length<limit&&!seen.has(id)){seen.add(id);selected.push(id);}});}
    return selected;
  }

  function nkNewStudyModuleDraft(){
    return {step:1,subjectIds:[activeSubject],topicIds:[],questionPoolType:'mixed',questionCount:20,countMode:20,name:'',nameEdited:false};
  }

  function openStudyModuleBuilder(){
    studyModuleDraft=nkNewStudyModuleDraft();navigate('module-builder');
  }

  function nkToggleModuleSubject(index){
    if(!studyModuleDraft)return;const record=SUBJECTS[index];if(!record)return;
    const selected=new Set(studyModuleDraft.subjectIds||[]);
    if(selected.has(record.subject)){if(selected.size===1){showToast('Keep at least one subject selected.','bad');return;}selected.delete(record.subject);studyModuleDraft.topicIds=(studyModuleDraft.topicIds||[]).filter(key=>!String(key).startsWith(`${record.subject}::`));}
    else selected.add(record.subject);
    studyModuleDraft.subjectIds=[...selected];render();
  }

  function nkToggleModuleTopic(subjectIndex,topicIndex){
    if(!studyModuleDraft)return;const record=SUBJECTS[subjectIndex],topic=nkModuleTopics(record)[topicIndex];if(!record||!topic)return;
    const key=nkModuleTopicKey(record.subject,topic.id),selected=new Set(studyModuleDraft.topicIds||[]);
    if(selected.has(key))selected.delete(key);else selected.add(key);studyModuleDraft.topicIds=[...selected];render();
  }

  function nkSetAllModuleTopics(select){
    if(!studyModuleDraft)return;
    const selected=select?new Set(studyModuleDraft.topicIds||[]):new Set();
    if(select)SUBJECTS.forEach(record=>{if((studyModuleDraft.subjectIds||[]).includes(record.subject))nkModuleTopics(record).forEach(topic=>selected.add(nkModuleTopicKey(record.subject,topic.id)));});
    studyModuleDraft.topicIds=[...selected];render();
  }

  function nkSetModulePool(type){
    if(!studyModuleDraft||!['unattempted','wrong','bookmarked','mixed'].includes(type))return;studyModuleDraft.questionPoolType=type;render();
  }

  function nkSetModuleCount(value){
    if(!studyModuleDraft)return;
    if(value==='custom'){studyModuleDraft.countMode='custom';studyModuleDraft.questionCount=Math.max(1,Number(studyModuleDraft.questionCount||30));}
    else{studyModuleDraft.countMode=Number(value);studyModuleDraft.questionCount=Number(value);}render();
  }

  function nkSetCustomModuleCount(value){
    if(!studyModuleDraft)return;studyModuleDraft.questionCount=Math.max(1,Math.min(500,Number(value||1)));
    const available=nkQuestionsForModuleDraft().length,node=document.getElementById('nk-module-availability');
    if(node)node.textContent=available?`${fmtNum(available)} eligible questions are currently available.`:'No eligible questions are available for this selection.';
  }

  function nkSetModuleName(value){if(studyModuleDraft){studyModuleDraft.name=String(value||'').slice(0,80);studyModuleDraft.nameEdited=true;}}

  function nkModuleBuilderStep(step){
    if(!studyModuleDraft)studyModuleDraft=nkNewStudyModuleDraft();
    if(step>studyModuleDraft.step){
      if(studyModuleDraft.step===1&&!studyModuleDraft.subjectIds.length){showToast('Select at least one subject.','bad');return;}
      if(studyModuleDraft.step===2&&!studyModuleDraft.topicIds.length){showToast('Select at least one topic.','bad');return;}
      if(studyModuleDraft.step===3&&!nkQuestionsForModuleDraft().length){showToast('Change the topics or question type to find eligible questions.','bad');return;}
    }
    studyModuleDraft.step=Math.max(1,Math.min(4,Number(step)));
    if(studyModuleDraft.step===4&&!studyModuleDraft.nameEdited)studyModuleDraft.name=nkStudyModuleAutoName();
    render();
  }

  function nkModuleBuilderSubjects(){
    return `<div class="nk-module-choice-grid">${SUBJECTS.map((record,index)=>{const selected=studyModuleDraft.subjectIds.includes(record.subject),stats=nkAppSubjectStats(record.subject),meta=nkAppSubjectMeta(record.subject);return `<button class="nk-module-subject is-${meta.key} ${selected?'is-selected':''}" onclick="window.QB.nkToggleModuleSubject(${index})"><span>${nkAppSubjectIcon(record.subject,23)}</span><strong>${esc(record.subject)}</strong><small>${fmtNum(stats.questions)} questions · ${fmtNum(stats.topics)} topics</small><i>${selected?navIcon('check',15):''}</i></button>`;}).join('')}</div>`;
  }

  function nkModuleBuilderTopics(){
    const groups=SUBJECTS.map((record,subjectIndex)=>{if(!studyModuleDraft.subjectIds.includes(record.subject))return'';const topics=nkModuleTopics(record);return `<section class="nk-module-topic-group"><header><span class="is-${nkAppSubjectMeta(record.subject).key}">${nkAppSubjectIcon(record.subject,18)}</span><div><strong>${esc(record.subject)}</strong><small>${topics.length} topics</small></div></header>${topics.map((topic,topicIndex)=>{const selected=studyModuleDraft.topicIds.includes(nkModuleTopicKey(record.subject,topic.id));return `<button class="nk-module-topic ${selected?'is-selected':''}" onclick="window.QB.nkToggleModuleTopic(${subjectIndex},${topicIndex})"><span class="nk-module-check">${selected?navIcon('check',13):''}</span><span><strong>${esc(topic.title)}</strong><small>${fmtNum(topic.questionCount)} questions</small></span></button>`;}).join('')}</section>`;}).join('');
    return `<div class="nk-module-select-tools"><button onclick="window.QB.nkSetAllModuleTopics(true)">Select all</button><button onclick="window.QB.nkSetAllModuleTopics(false)">Clear selection</button><span>${studyModuleDraft.topicIds.length} selected</span></div><div class="nk-module-topic-groups">${groups}</div>`;
  }

  function nkModuleBuilderPool(){
    const available=nkQuestionsForModuleDraft().length,requested=Math.max(1,Number(studyModuleDraft.questionCount||20));
    const types=[['unattempted','Unattempted','Questions you have not answered'],['wrong','Wrong','Questions missed before'],['bookmarked','Bookmarked','Questions you saved'],['mixed','Mixed','Prioritises wrong and unattempted']];
    const countButtons=[10,20,30].map(count=>`<button class="${studyModuleDraft.countMode===count?'is-selected':''}" onclick="window.QB.nkSetModuleCount(${count})">${count}</button>`).join('');
    const warning=!available?'No eligible questions are available for the selected topics and question type.':requested>available?`You requested ${requested}. ${available} eligible questions are currently available. The module will use all ${available}.`:`${available} eligible questions are currently available.`;
    return `<div class="nk-module-pool-grid">${types.map(([value,title,copy])=>`<button class="${studyModuleDraft.questionPoolType===value?'is-selected':''}" onclick="window.QB.nkSetModulePool('${value}')"><strong>${title}</strong><small>${copy}</small></button>`).join('')}</div><div class="nk-module-count-block"><strong>Question count</strong><div class="nk-module-count-presets">${countButtons}<button class="${studyModuleDraft.countMode==='custom'?'is-selected':''}" onclick="window.QB.nkSetModuleCount('custom')">Custom</button></div>${studyModuleDraft.countMode==='custom'?`<label>Custom count<input type="number" min="1" max="500" value="${requested}" oninput="window.QB.nkSetCustomModuleCount(this.value)"></label>`:''}<p id="nk-module-availability" class="${available?'':'is-error'}">${esc(warning)}</p></div>`;
  }

  function nkModuleBuilderReview(){
    const available=nkQuestionsForModuleDraft().length,requested=Math.max(1,Number(studyModuleDraft.questionCount||20)),actual=Math.min(requested,available),autoName=nkStudyModuleAutoName();
    return `<label class="nk-module-name"><span>Module name</span><input maxlength="80" value="${esc(studyModuleDraft.name||autoName)}" placeholder="${esc(autoName)}" oninput="window.QB.nkSetModuleName(this.value)"></label><div class="nk-module-review-card"><div><small>Study scope</small><strong>${esc((studyModuleDraft.subjectIds||[]).join(' + '))}</strong><p>${fmtNum(studyModuleDraft.topicIds.length)} topics selected</p></div><div><small>Question pool</small><strong>${esc(nkStudyModulePoolLabel(studyModuleDraft.questionPoolType))}</strong><p>${fmtNum(actual)} questions</p></div></div>${requested>available?`<div class="nk-module-warning">Only ${fmtNum(available)} eligible questions are available. You can create this module with all ${fmtNum(actual)} questions.</div>`:''}`;
  }

  function studyModuleBuilderPage(){
    if(!studyModuleDraft)studyModuleDraft=nkNewStudyModuleDraft();
    const step=studyModuleDraft.step||1,titles=['Choose subjects','Choose topics','Build question pool','Name and create'];
    const content=step===1?nkModuleBuilderSubjects():step===2?nkModuleBuilderTopics():step===3?nkModuleBuilderPool():nkModuleBuilderReview();
    const available=nkQuestionsForModuleDraft().length,canCreate=available>0&&studyModuleDraft.topicIds.length>0;
    return shell(`<div class="nk-app-v114 nk-module-builder"><button class="nk-back-link" onclick="${step===1?"window.QB.nav('dashboard')":`window.QB.nkModuleBuilderStep(${step-1})`}">${navIcon('back',18)} ${step===1?'Home':'Back'}</button>${nkAppPageHead(`CUSTOM STUDY · STEP ${step} OF 4`,titles[step-1],'Build a focused set that stays stable while you work through it.')}<div class="nk-module-stepper">${[1,2,3,4].map(n=>`<span class="${n===step?'is-current':n<step?'is-done':''}"><i>${n<step?navIcon('check',12):n}</i><b>${['Subjects','Topics','Questions','Finish'][n-1]}</b></span>`).join('')}</div><section class="nk-module-builder-card">${content}</section><div class="nk-module-builder-actions">${step>1?`<button onclick="window.QB.nkModuleBuilderStep(${step-1})">Back</button>`:'<span></span>'}${step<4?`<button class="is-primary" onclick="window.QB.nkModuleBuilderStep(${step+1})">Continue</button>`:`<div class="nk-module-final-actions"><button ${canCreate?'':'disabled'} onclick="window.QB.nkCreateStudyModule(false)">Save for later</button><button class="is-primary" ${canCreate?'':'disabled'} onclick="window.QB.nkCreateStudyModule(true)">Start now</button></div>`}</div></div>`,'dashboard');
  }

  function nkCreateStudyModule(startNow){
    if(!studyModuleDraft)return;const available=nkQuestionsForModuleDraft().length;if(!available){showToast('No eligible questions are available. Change your filters.','bad');return;}
    const now=Date.now(),id=`module_${now}_${Math.random().toString(16).slice(2)}`,questionIds=nkSelectModuleQuestionIds(studyModuleDraft,id);
    if(!questionIds.length){showToast('No eligible questions are available. Change your filters.','bad');return;}
    const module=nkNormalizeStudyModule({id,name:(studyModuleDraft.name||nkStudyModuleAutoName()).trim(),subjectIds:[...studyModuleDraft.subjectIds],topicIds:[...studyModuleDraft.topicIds],questionPoolType:studyModuleDraft.questionPoolType,questionIds,totalQuestions:questionIds.length,completedQuestionIds:[],currentPosition:0,answers:{},submitted:{},questionTimes:{},createdAt:now,lastOpenedAt:now,completedAt:null,isCompleted:false,resultTestId:null});
    state.studyModules=[...nkStudyModuleList(),module].slice(-100);studyModuleDraft=null;saveState();
    if(startNow)startStudyModule(module.id);else{showToast('Study module saved.','good');navigate('dashboard');}
  }

  function startStudyModule(id){
    const module=nkFindStudyModule(id);if(!module)return;
    if(module.isCompleted&&module.resultTestId){navigate('result',module.resultTestId);return;}
    const ids=nkModuleValidQuestionIds(module);
    if(!ids.length){showToast('The questions in this module are no longer available.','bad');return;}
    const submitted={...(module.submitted||{})},firstRemaining=ids.findIndex(qid=>!submitted[qid]);
    const index=firstRemaining>=0?firstRemaining:Math.min(Math.max(0,module.currentPosition||0),ids.length-1),now=Date.now();
    state.activeSession={id:`s_${now}_${Math.random().toString(16).slice(2)}`,mode:'practice',title:module.name,questionIds:ids,index,answers:{...(module.answers||{})},submitted,startedAt:now,lastTick:now,elapsedMs:0,questionEnteredAt:now,questionTimes:{...(module.questionTimes||{})},context:'study-module',studyModuleId:module.id};
    module.lastOpenedAt=now;if(!state.studyStartedAt)state.studyStartedAt=now;saveState();navigate('practice');
  }

  function exitStudyModule(){
    const s=state.activeSession;if(!s?.studyModuleId)return;nkSyncModuleFromSession();state.activeSession=null;saveState();navigate('dashboard');showToast('Module progress saved.','good');
  }

  function nkCompleteStudyModule(moduleId,test){
    const module=nkFindStudyModule(moduleId);if(!module)return;
    nkSyncModuleFromSession();module.isCompleted=true;module.completedAt=Date.now();module.lastOpenedAt=Date.now();module.resultTestId=String(test.id);module.currentPosition=Math.max(0,module.questionIds.length-1);
    test.studyModuleId=module.id;test.kind='practice';
  }

  function finishStudyModuleEarly(){
    const s=state.activeSession;if(!s?.studyModuleId)return;
    const remaining=s.questionIds.filter(id=>!s.submitted?.[id]).length;
    if(remaining&&!confirm(`Finish this module with ${remaining} unanswered question${remaining===1?'':'s'}?`))return;
    closeSessionReview();finishPracticeSession();
  }

  function restartStudyModule(id){
    const module=nkFindStudyModule(id);if(!module)return;
    if(!confirm(`Restart ${module.name}? Its saved question set will stay the same, but module progress will reset.`))return;
    module.completedQuestionIds=[];module.currentPosition=0;module.answers={};module.submitted={};module.questionTimes={};module.completedAt=null;module.isCompleted=false;module.resultTestId=null;module.lastOpenedAt=Date.now();saveState();startStudyModule(module.id);
  }

  function renameStudyModule(id){
    const module=nkFindStudyModule(id);if(!module)return;const name=prompt('Rename study module',module.name);if(name===null)return;const clean=String(name).trim().slice(0,80);if(!clean){showToast('Module name cannot be empty.','bad');return;}module.name=clean;module.lastOpenedAt=Date.now();saveState();render();
  }

  function deleteStudyModule(id){
    const module=nkFindStudyModule(id);if(!module)return;if(!confirm(`Delete ${module.name}? Your question attempt history will remain.`))return;
    state.studyModules=nkStudyModuleList().filter(item=>String(item.id)!==String(id));if(state.activeSession?.studyModuleId===id)state.activeSession=null;saveState();render();showToast('Study module deleted.');
  }

  function nkPriorityStudyModule(){
    return nkStudyModuleList().filter(module=>!module.isCompleted&&nkModuleProgress(module).remaining>0).sort((a,b)=>Number(b.lastOpenedAt||b.createdAt||0)-Number(a.lastOpenedAt||a.createdAt||0))[0]||null;
  }

  function nkStudyModuleCard(module){
    const progress=nkModuleProgress(module),pct=progress.total?Math.round(progress.completed/progress.total*100):0;
    return `<article class="nk-study-set-card"><div class="nk-study-set-main"><span class="nk-study-set-icon">${navIcon('book',19)}</span><div><strong>${esc(module.name)}</strong><small>${esc(nkStudyModuleTopicSummary(module))}</small><em>${esc(nkStudyModulePoolLabel(module.questionPoolType))}</em></div><details><summary aria-label="Manage ${esc(module.name)}">${navIcon('more',18)}</summary><div><button onclick="window.QB.renameStudyModule('${esc(module.id)}')">Rename</button><button onclick="window.QB.restartStudyModule('${esc(module.id)}')">Restart</button><button class="is-danger" onclick="window.QB.deleteStudyModule('${esc(module.id)}')">Delete</button></div></details></div><div class="nk-study-set-progress"><span><b>${progress.completed} / ${progress.total}</b> completed</span><span>${progress.remaining} question${progress.remaining===1?'':'s'} left</span></div><span class="nk-line-progress"><i style="width:${pct}%"></i></span>${progress.missing?`<p>${progress.missing} unavailable question${progress.missing===1?' was':'s were'} skipped.</p>`:''}<button class="nk-study-set-action" onclick="window.QB.startStudyModule('${esc(module.id)}')">${module.isCompleted?'View results':'Continue'} ${navIcon('chevron',16)}</button></article>`;
  }

  function nkStudySetsSection(){
    const modules=nkStudyModuleList().slice().sort((a,b)=>Number(b.lastOpenedAt||b.createdAt||0)-Number(a.lastOpenedAt||a.createdAt||0));
    return `<section class="nk-section nk-study-sets"><div class="nk-section-head"><div><div class="nk-kicker">INTENTIONAL STUDY</div><h2>My study sets</h2></div><button class="nk-text-link" onclick="window.QB.openStudyModuleBuilder()">Create module ${navIcon('chevron',15)}</button></div>${modules.length?`<div class="nk-study-set-list">${modules.slice(0,4).map(nkStudyModuleCard).join('')}</div>`:`<div class="nk-study-set-empty"><span>${navIcon('book',22)}</span><div><strong>Build your first focused module</strong><p>Choose subjects, topics, and the exact kind of questions you need.</p></div><button onclick="window.QB.openStudyModuleBuilder()">Create module</button></div>`}</section>`;
  }

  function nkStudyModuleSessionContext(s){
    const module=nkFindStudyModule(s.studyModuleId),progress=module?nkModuleProgress(module):{remaining:0};
    return `<div class="nk-module-session-context"><span>${navIcon('book',18)}</span><div><small>STUDY MODULE</small><strong>${esc(module?.name||s.title)}</strong></div><em>${s.index+1} of ${s.questionIds.length}</em></div>`;
  }

  function nkModuleResultExtras(test,module){
    const rows=new Map();
    (test.questionIds||[]).forEach(id=>{const q=BY_ID[id];if(!q)return;const key=`${q.subject||'Biochemistry'}::${q.chapterId}`,row=rows.get(key)||{title:q.chapter,total:0,correct:0};row.total++;if(test.answers?.[id]&&Number(test.answers[id])===Number(q.correctOption))row.correct++;rows.set(key,row);});
    return `<section class="nk-section nk-module-result"><div class="nk-section-head"><div><div class="nk-kicker">STUDY MODULE COMPLETE</div><h2>${esc(module.name)}</h2></div></div><div class="nk-module-result-actions"><button onclick="window.__QB_OPEN_REVIEW('${esc(test.id)}')">Review Solutions</button><button onclick="window.QB.restartStudyModule('${esc(module.id)}')">Restart module</button><button onclick="window.QB.nav('dashboard')">Return Home</button></div><div class="nk-performance-list">${[...rows.values()].map(row=>`<div class="nk-module-topic-result"><span><strong>${esc(row.title)}</strong><small>${row.correct} of ${row.total} correct</small></span><b>${fmtPct(row.total?row.correct/row.total*100:0)}</b></div>`).join('')}</div></section>`;
  }
/* NK_CUSTOM_STUDY_MODULES_V1_END */
