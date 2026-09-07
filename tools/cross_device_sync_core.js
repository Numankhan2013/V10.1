/* NK_CROSS_DEVICE_SYNC_V1_START
 * Inserted into the canonical app IIFE. Dependencies are existing QBank globals:
 * state, saveState, render, showToast, activeSubject, applySubject, fmtDate, esc.
 */
  const NK_SYNC_META_KEY='qbank_sync_v1';
  const NK_AUTH_KEY='qbank_firebase_auth_v1';
  const NK_PRE_CLOUD_BACKUP='qbank_state_pre_cloud_v1';
  const NK_SYNC_KINDS=['attempts','bookmarks','tests','modules','sessions','preferences'];
  let nkCloudBusy=false,nkCloudReady=false,nkCloudTimer=null;

  function nkJson(value,fallback){try{return JSON.parse(value);}catch(_){return fallback;}}
  function nkStable(value){
    if(Array.isArray(value))return '['+value.map(nkStable).join(',')+']';
    if(value&&typeof value==='object')return '{'+Object.keys(value).sort().map(k=>JSON.stringify(k)+':'+nkStable(value[k])).join(',')+'}';
    return JSON.stringify(value);
  }
  function nkHash(value){let h=2166136261,s=nkStable(value);for(let i=0;i<s.length;i++){h^=s.charCodeAt(i);h=Math.imul(h,16777619);}return (h>>>0).toString(36);}
  function nkLoadSyncMeta(){
    const value=nkJson(localStorage.getItem(NK_SYNC_META_KEY),{})||{};
    value.deviceId=value.deviceId||`device_${Date.now().toString(36)}_${Math.random().toString(36).slice(2,10)}`;
    value.outbox=value.outbox&&typeof value.outbox==='object'?value.outbox:{};
    value.localHashes=value.localHashes&&typeof value.localHashes==='object'?value.localHashes:{};
    value.known=value.known&&typeof value.known==='object'?value.known:{};
    value.winners=value.winners&&typeof value.winners==='object'?value.winners:{};
    value.cursors=value.cursors&&typeof value.cursors==='object'?value.cursors:{};
    return value;
  }
  let nkSyncMeta=nkLoadSyncMeta();
  function nkSaveSyncMeta(){try{localStorage.setItem(NK_SYNC_META_KEY,JSON.stringify(nkSyncMeta));}catch(_){}}
  nkSaveSyncMeta();

  function nkFirebaseConfig(){const c=window.NK_QBANK_FIREBASE_CONFIG||{};return {apiKey:String(c.apiKey||''),projectId:String(c.projectId||''),anatomyPdfUrl:String(c.anatomyPdfUrl||'')};}
  function nkCloudConfigured(){const c=nkFirebaseConfig();return Boolean(c.apiKey&&c.projectId);}
  function nkLoadAuth(){const a=nkJson(localStorage.getItem(NK_AUTH_KEY),null);return a&&a.refreshToken&&a.uid?a:null;}
  var nkAuth=nkLoadAuth();
  function nkSaveAuth(){if(nkAuth)localStorage.setItem(NK_AUTH_KEY,JSON.stringify(nkAuth));else localStorage.removeItem(NK_AUTH_KEY);}
  function nkAuthValid(){return Boolean(nkAuth?.idToken&&Number(nkAuth.expiresAt||0)>Date.now()+60000);}

  async function nkFetchJson(url,options={}){
    const response=await fetch(url,options),text=await response.text(),body=nkJson(text,{});
    if(!response.ok){const error=new Error(body?.error?.message||body?.error?.status||`Request failed (${response.status})`);error.status=response.status;throw error;}
    return body;
  }
  async function nkRefreshAuth(){
    if(!nkAuth?.refreshToken)throw new Error('Sign in to synchronize.');
    if(nkAuthValid())return nkAuth.idToken;
    const c=nkFirebaseConfig(),body=new URLSearchParams({grant_type:'refresh_token',refresh_token:nkAuth.refreshToken});
    const data=await nkFetchJson(`https://securetoken.googleapis.com/v1/token?key=${encodeURIComponent(c.apiKey)}`,{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded'},body:String(body)});
    nkAuth={...nkAuth,uid:String(data.user_id),idToken:String(data.id_token),refreshToken:String(data.refresh_token||nkAuth.refreshToken),expiresAt:Date.now()+Number(data.expires_in||3600)*1000};nkSaveAuth();return nkAuth.idToken;
  }
  function nkAuthMessage(code){return ({EMAIL_EXISTS:'That email already has an account.',EMAIL_NOT_FOUND:'No account was found for that email.',INVALID_PASSWORD:'The password is incorrect.',INVALID_LOGIN_CREDENTIALS:'The email or password is incorrect.',WEAK_PASSWORD:'Use a password with at least 6 characters.',TOO_MANY_ATTEMPTS_TRY_LATER:'Too many attempts. Please try again later.'})[String(code).split(' : ')[0]]||String(code).replaceAll('_',' ').toLowerCase();}
  async function nkCloudAuthenticate(mode){
    if(!nkCloudConfigured()){showToast('Firebase is not configured for this build.','bad');return;}
    const email=String(document.getElementById('nk-cloud-email')?.value||'').trim(),password=String(document.getElementById('nk-cloud-password')?.value||'');
    if(!email||password.length<6){showToast('Enter your email and a password of at least 6 characters.','bad');return;}
    try{
      const c=nkFirebaseConfig(),action=mode==='create'?'signUp':'signInWithPassword';
      const data=await nkFetchJson(`https://identitytoolkit.googleapis.com/v1/accounts:${action}?key=${encodeURIComponent(c.apiKey)}`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email,password,returnSecureToken:true})});
      if(nkSyncMeta.boundUid&&nkSyncMeta.boundUid!==String(data.localId))throw new Error('This installation is already linked to a different QBank account.');
      nkAuth={uid:String(data.localId),email:String(data.email||email),idToken:String(data.idToken),refreshToken:String(data.refreshToken),expiresAt:Date.now()+Number(data.expiresIn||3600)*1000};nkSaveAuth();
      nkSyncMeta.boundUid=nkAuth.uid;nkSaveSyncMeta();
      await nkInitialCloudSync();showToast(mode==='create'?'Account created and progress synchronized.':'Signed in and synchronized.','good');render();
    }catch(error){showToast(nkAuthMessage(error.message),'bad');}
  }
  function nkCloudSignOut(){nkAuth=null;nkCloudReady=false;nkSaveAuth();showToast('Signed out. Your synchronized progress remains on this device.');render();}

  function nkEnvelope(kind,entityId,payload,updatedAt,deleted=false){return {kind,entityId:String(entityId),ownerDevice:nkSyncMeta.deviceId,updatedAt:Math.max(1,Number(updatedAt||Date.now())),deleted:Boolean(deleted),payload:deleted?'':JSON.stringify(payload),schemaVersion:1};}
  function nkQueueEnvelope(envelope){
    const key=`${envelope.kind}/${envelope.entityId}`,signature=nkHash({deleted:envelope.deleted,payload:envelope.payload});
    if(nkSyncMeta.localHashes[key]===signature)return;
    nkSyncMeta.localHashes[key]=signature;envelope.updatedAt=Math.max(Date.now(),Number(envelope.updatedAt||0));nkSyncMeta.outbox[key]=envelope;
  }
  function nkEntityTimestamp(value,fallback=0){return Math.max(Number(value?.updatedAt||0),Number(value?.lastOpenedAt||0),Number(value?.completedAt||0),Number(value?.createdAt||0),Number(value?.questionEnteredAt||0),Number(value?.lastTick||0),Number(value?.startedAt||0),Number(fallback||0));}
  function nkCaptureCloudChanges(){
    if(!nkAuth)return;
    const current={bookmarks:new Set(),modules:new Set()};
    Object.entries(state.attempts||{}).forEach(([qid,list])=>(Array.isArray(list)?list:[]).forEach(attempt=>{if(attempt?.id)nkQueueEnvelope(nkEnvelope('attempts',attempt.id,{qid:String(qid),attempt},Number(attempt.at||0)));}));
    Object.entries(state.bookmarks||{}).forEach(([qid,value])=>{current.bookmarks.add(String(qid));nkQueueEnvelope(nkEnvelope('bookmarks',qid,{qid:String(qid),active:true},Number(value?.updatedAt||value?.addedAt||0)));});
    (state.tests||[]).forEach(test=>{if(test?.id)nkQueueEnvelope(nkEnvelope('tests',test.id,test,nkEntityTimestamp(test)));});
    (state.studyModules||[]).forEach(module=>{if(!module?.id)return;current.modules.add(String(module.id));if(!module.syncEpoch)module.syncEpoch=`epoch_${module.createdAt||Date.now()}`;nkQueueEnvelope(nkEnvelope('modules',module.id,module,nkEntityTimestamp(module)));});
    for(const kind of ['bookmarks','modules']){
      const before=new Set(Array.isArray(nkSyncMeta.known[kind])?nkSyncMeta.known[kind]:[]);
      before.forEach(id=>{if(!current[kind].has(id))nkQueueEnvelope(nkEnvelope(kind,id,null,Date.now(),true));});
      nkSyncMeta.known[kind]=[...current[kind]];
    }
    nkQueueEnvelope(nkEnvelope('sessions','active',state.activeSession||null,nkEntityTimestamp(state.activeSession,Date.now()),!state.activeSession));
    nkQueueEnvelope(nkEnvelope('preferences','main',{activeSubject,studyStartedAt:state.studyStartedAt||null},Date.now()));
    nkSaveSyncMeta();nkScheduleCloudFlush();
  }
  function nkScheduleCloudSync(){if(!nkAuth)return;nkCaptureCloudChanges();}
  function nkScheduleCloudFlush(){clearTimeout(nkCloudTimer);nkCloudTimer=setTimeout(()=>nkCloudSync(false),1200);}

  function nkFirestoreValue(value){
    if(typeof value==='boolean')return {booleanValue:value};
    if(typeof value==='number')return {integerValue:String(Math.trunc(value))};
    return {stringValue:String(value??'')};
  }
  function nkFirestoreDocument(envelope,docName){const fields={};Object.entries(envelope).forEach(([key,value])=>fields[key]=nkFirestoreValue(value));return {name:docName,fields};}
  function nkDecodeDocument(doc){const f=doc?.fields||{},read=k=>f[k]?.stringValue??f[k]?.integerValue??f[k]?.booleanValue;return {kind:String(read('kind')||''),entityId:String(read('entityId')||''),ownerDevice:String(read('ownerDevice')||''),updatedAt:Number(read('updatedAt')||0),deleted:Boolean(read('deleted')),payload:String(read('payload')||''),schemaVersion:Number(read('schemaVersion')||0)};}
  function nkFirestoreRoot(){const c=nkFirebaseConfig();return `https://firestore.googleapis.com/v1/projects/${encodeURIComponent(c.projectId)}/databases/(default)/documents`;}
  function nkDocId(envelope){return encodeURIComponent(`${envelope.ownerDevice}--${envelope.entityId}`);}
  async function nkPushOutbox(token){
    const entries=Object.entries(nkSyncMeta.outbox||{});if(!entries.length)return 0;
    let sent=0;
    for(let i=0;i<entries.length;i+=200){
      const batch=entries.slice(i,i+200),writes=batch.map(([,e])=>{const name=`projects/${nkFirebaseConfig().projectId}/databases/(default)/documents/users/${nkAuth.uid}/${e.kind}/${nkDocId(e)}`;return {update:nkFirestoreDocument(e,name)};});
      const result=await nkFetchJson(`${nkFirestoreRoot()}:batchWrite`,{method:'POST',headers:{Authorization:`Bearer ${token}`,'Content-Type':'application/json'},body:JSON.stringify({writes})});
      const failed=(result.status||[]).find(status=>Number(status?.code||0)!==0);if(failed)throw new Error(failed.message||'A synchronized write was rejected.');
      batch.forEach(([key])=>delete nkSyncMeta.outbox[key]);sent+=batch.length;nkSaveSyncMeta();
    }
    return sent;
  }
  async function nkPullKind(kind,token){
    const cursor=Math.max(0,Number(nkSyncMeta.cursors[kind]||0)),structuredQuery={from:[{collectionId:kind}],orderBy:[{field:{fieldPath:'updatedAt'},direction:'ASCENDING'}]};
    if(cursor)structuredQuery.where={fieldFilter:{field:{fieldPath:'updatedAt'},op:'GREATER_THAN_OR_EQUAL',value:{integerValue:String(Math.max(0,cursor-1))}}};
    const rows=await nkFetchJson(`${nkFirestoreRoot()}/users/${encodeURIComponent(nkAuth.uid)}:runQuery`,{method:'POST',headers:{Authorization:`Bearer ${token}`,'Content-Type':'application/json'},body:JSON.stringify({structuredQuery})});
    const docs=(Array.isArray(rows)?rows:[]).map(row=>row.document).filter(Boolean).map(nkDecodeDocument).filter(e=>e.schemaVersion===1&&e.kind===kind);
    if(docs.length)nkSyncMeta.cursors[kind]=Math.max(cursor,...docs.map(e=>e.updatedAt));
    return docs;
  }
  function nkWinnerKey(e){return `${e.kind}/${e.entityId}`;}
  function nkChooseWinner(remote){
    const key=nkWinnerKey(remote),saved=nkSyncMeta.winners[key],pending=nkSyncMeta.outbox[key],candidates=[remote,saved,pending].filter(Boolean);
    candidates.sort((a,b)=>Number(b.updatedAt||0)-Number(a.updatedAt||0)||String(b.ownerDevice||'').localeCompare(String(a.ownerDevice||'')));
    const winner=candidates[0];nkSyncMeta.winners[key]=winner;return winner;
  }
  function nkRebuildReviews(){
    const intervals=[0.0069,0.04,1,3,7,14,30],reviews={};
    Object.entries(state.attempts||{}).forEach(([qid,list])=>{
      let streak=0,count=0,last=0,interval=0;
      [...(Array.isArray(list)?list:[])].sort((a,b)=>Number(a.at||0)-Number(b.at||0)).forEach(a=>{count++;last=Number(a.at||last);streak=a.correct?Math.min(streak+1,6):0;interval=a.correct?intervals[streak]:intervals[0];});
      if(count)reviews[qid]={attempts:count,streak,intervalDays:interval,lastReviewedAt:last,nextReviewAt:last+interval*86400000};
    });state.reviews=reviews;
  }
  function nkApplyCloudEnvelope(remote){
    const winner=remote.kind==='attempts'?remote:nkChooseWinner(remote);if(winner!==remote&&nkHash(winner)!==nkHash(remote))return false;
    const payload=winner.deleted?null:nkJson(winner.payload,null),id=winner.entityId;
    if(winner.kind==='attempts'&&payload?.attempt?.id){const qid=String(payload.qid),list=Array.isArray(state.attempts[qid])?state.attempts[qid]:[];if(!list.some(a=>String(a.id)===String(payload.attempt.id)))state.attempts[qid]=[...list,payload.attempt].sort((a,b)=>Number(a.at||0)-Number(b.at||0));}
    else if(winner.kind==='bookmarks'){if(winner.deleted||!payload?.active)delete state.bookmarks[id];else state.bookmarks[id]={addedAt:Number(winner.updatedAt),updatedAt:Number(winner.updatedAt)};}
    else if(winner.kind==='tests'&&payload){const index=(state.tests||[]).findIndex(x=>String(x.id)===id);if(index<0)state.tests.push(payload);else state.tests[index]=payload;state.tests=state.tests.slice(-100);}
    else if(winner.kind==='modules'){
      const list=Array.isArray(state.studyModules)?state.studyModules:[],index=list.findIndex(x=>String(x.id)===id),local=index>=0?list[index]:null;
      if(winner.deleted){if(index>=0)list.splice(index,1);}
      else if(payload){
        let merged=payload;
        if(local&&String(local.syncEpoch||'')===String(payload.syncEpoch||'')){
          const submitted={...(local.submitted||{}),...(payload.submitted||{})},answers={...(local.answers||{}),...(payload.answers||{})},questionTimes={...(local.questionTimes||{})};
          Object.entries(payload.questionTimes||{}).forEach(([qid,time])=>questionTimes[qid]=Math.max(Number(questionTimes[qid]||0),Number(time||0)));
          const completedQuestionIds=[...new Set([...(local.completedQuestionIds||[]),...(payload.completedQuestionIds||[]),...Object.keys(submitted).filter(qid=>submitted[qid])])];
          merged={...payload,submitted,answers,questionTimes,completedQuestionIds,isCompleted:Boolean(local.isCompleted||payload.isCompleted),completedAt:Math.max(Number(local.completedAt||0),Number(payload.completedAt||0))||null};
        }
        if(index<0)list.push(merged);else list[index]=merged;
      }state.studyModules=list.slice(-100);
    }
    else if(winner.kind==='sessions'){state.activeSession=winner.deleted?null:payload;}
    else if(winner.kind==='preferences'&&payload){if(payload.activeSubject&&typeof SUBJECT_BY_NAME!=='undefined'&&SUBJECT_BY_NAME[payload.activeSubject])applySubject(payload.activeSubject);if(payload.studyStartedAt)state.studyStartedAt=state.studyStartedAt?Math.min(Number(state.studyStartedAt),Number(payload.studyStartedAt)):Number(payload.studyStartedAt);}
    return true;
  }
  async function nkPullCloud(token){let count=0;for(const kind of NK_SYNC_KINDS){const docs=await nkPullKind(kind,token);docs.forEach(doc=>{nkApplyCloudEnvelope(doc);count++;});}nkRebuildReviews();if(typeof nkNormalizeStudyModules==='function')nkNormalizeStudyModules();return count;}
  async function nkInitialCloudSync(){
    if(!localStorage.getItem(NK_PRE_CLOUD_BACKUP)){const raw=localStorage.getItem(LS_KEY);if(raw)localStorage.setItem(NK_PRE_CLOUD_BACKUP,raw);}
    nkCloudReady=false;await nkCloudSync(true);nkCloudReady=true;nkCaptureCloudChanges();
  }
  async function nkCloudSync(initial=false){
    if(nkCloudBusy||!nkAuth||!nkCloudConfigured())return false;clearTimeout(nkCloudTimer);nkCloudBusy=true;nkSyncMeta.status='syncing';render();
    try{
      const token=await nkRefreshAuth(),pulled=await nkPullCloud(token);
      localStorage.setItem(LS_KEY,JSON.stringify(state));
      if(initial){nkCloudReady=true;nkCaptureCloudChanges();}
      const pushed=await nkPushOutbox(token);nkSyncMeta.lastSyncAt=Date.now();nkSyncMeta.status='synced';nkSyncMeta.lastError='';nkSaveSyncMeta();render();return {pulled,pushed};
    }catch(error){nkSyncMeta.status=navigator.onLine?'error':'offline';nkSyncMeta.lastError=String(error.message||error);nkSaveSyncMeta();if(!initial)showToast(navigator.onLine?'Sync paused. Your progress is safe on this device.':'Offline. Changes will sync when connected.','bad');render();return false;}
    finally{nkCloudBusy=false;}
  }
  async function nkCloudSyncNow(){if(!nkAuth){showToast('Sign in to synchronize.','bad');return;}nkCaptureCloudChanges();await nkCloudSync(false);if(nkSyncMeta.status==='synced')showToast('Progress is up to date.','good');}
  function nkCloudStatusCopy(){if(!navigator.onLine)return 'Offline · changes stay on this device';if(nkCloudBusy||nkSyncMeta.status==='syncing')return 'Synchronizing…';if(nkSyncMeta.status==='error')return 'Sync paused · tap Sync now';if(nkSyncMeta.lastSyncAt)return `Synced ${fmtDate(nkSyncMeta.lastSyncAt)}`;return 'Ready to synchronize';}
  function nkCloudAccountCard(){
    const pwa=location.hostname==='qbank.local'?'Android app':'Install from Safari with Share → Add to Home Screen.';
    if(!nkCloudConfigured())return `<section class="nk-settings-group"><div class="nk-kicker">CROSS-DEVICE</div><div class="card pad nk-cloud-card"><div class="section-title"><span>QBank Sync</span><span class="sub">Not configured</span></div><p class="small-muted">This build keeps all progress locally. Add the Firebase public configuration to enable secure account sync.</p><div class="nk-cloud-pwa">${esc(pwa)}</div></div></section>`;
    if(!nkAuth)return `<section class="nk-settings-group"><div class="nk-kicker">CROSS-DEVICE</div><div class="card pad nk-cloud-card"><div class="section-title"><span>QBank Sync</span><span class="sub">Firebase</span></div><p class="small-muted">Use the same private account on Android and iPad. Existing progress is backed up before its first merge.</p><label>Email<input id="nk-cloud-email" type="email" autocomplete="username" inputmode="email"></label><label>Password<input id="nk-cloud-password" type="password" autocomplete="current-password" minlength="6"></label><div class="nk-cloud-actions"><button onclick="window.QB.nkCloudAuthenticate('signin')">Sign in</button><button class="primary-btn" onclick="window.QB.nkCloudAuthenticate('create')">Create account</button></div><div class="nk-cloud-pwa">${esc(pwa)}</div></div></section>`;
    return `<section class="nk-settings-group"><div class="nk-kicker">CROSS-DEVICE</div><div class="card pad nk-cloud-card"><div class="nk-cloud-user"><span class="nk-cloud-dot ${nkSyncMeta.status==='error'?'is-error':navigator.onLine?'is-online':''}"></span><div><strong>${esc(nkAuth.email||'QBank account')}</strong><small>${esc(nkCloudStatusCopy())}</small></div></div><p class="small-muted">Attempts, bookmarks, tests, modules, active sessions and study preferences merge without replacing newer device data.</p><div class="nk-cloud-actions"><button class="primary-btn" onclick="window.QB.nkCloudSyncNow()">Sync now</button><button onclick="window.QB.nkCloudSignOut()">Sign out</button></div><div class="nk-cloud-pwa">${esc(pwa)}</div></div></section>`;
  }
  async function nkCloudInit(){
    window.addEventListener('online',()=>{if(nkAuth)nkCloudSync(false);});
    window.addEventListener('offline',()=>{nkSyncMeta.status='offline';nkSaveSyncMeta();render();});
    if(!nkAuth||!nkCloudConfigured())return;
    try{await nkInitialCloudSync();}catch(_){nkCloudReady=true;}
  }
/* NK_CROSS_DEVICE_SYNC_V1_END */
