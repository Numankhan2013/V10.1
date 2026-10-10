  /* NK_NOTE_MEDIA_V1_START
   * Images and PDF pages inside question notes. Bytes live in IndexedDB, never in
   * the localStorage study state. Each asset uploads once and downloads once per
   * device through its own Firestore documents, outside the five-minute envelope pull.
   */
  const NK_NOTE_PDF_IMPORT_LIMIT=10;
  const NK_NOTE_FULL_EDGE=3200,NK_NOTE_PREVIEW_EDGE=1400,NK_NOTE_THUMB_EDGE=360;
  const NK_NOTE_MAX_BYTES=3500000,NK_NOTE_MAX_PIXELS=16000000;
  // Firestore rules cap one payload at 900000 characters; leave room for the JSON wrapper.
  const NK_NOTE_CHUNK_CHARS=800000;
  const NK_NOTE_DB_NAME='qbank_note_media_v1',NK_NOTE_STORES=['meta','full','preview','thumb'];

  /* ---------- IndexedDB ---------- */
  let nkNoteDbPromise=null;
  function nkNoteDb(){
    if(nkNoteDbPromise)return nkNoteDbPromise;
    nkNoteDbPromise=new Promise((resolve,reject)=>{
      if(typeof indexedDB==='undefined'||!indexedDB){reject(new Error('This browser cannot store note images.'));return;}
      const request=indexedDB.open(NK_NOTE_DB_NAME,1);
      request.onupgradeneeded=()=>{const db=request.result;NK_NOTE_STORES.forEach(name=>{if(!db.objectStoreNames.contains(name))db.createObjectStore(name,{keyPath:'id'});});};
      request.onsuccess=()=>{const db=request.result;db.onversionchange=()=>{db.close();nkNoteDbPromise=null;};resolve(db);};
      request.onerror=()=>reject(request.error||new Error('Note image storage is unavailable.'));
      request.onblocked=()=>reject(new Error('Close other QBank windows to open note images.'));
    });
    nkNoteDbPromise.catch(()=>{nkNoteDbPromise=null;});
    return nkNoteDbPromise;
  }
  function nkNoteIdbRequest(request){return new Promise((resolve,reject)=>{request.onsuccess=()=>resolve(request.result);request.onerror=()=>reject(request.error);});}
  async function nkNoteIdbGet(store,id){const db=await nkNoteDb();return nkNoteIdbRequest(db.transaction(store,'readonly').objectStore(store).get(String(id)));}
  async function nkNoteIdbAll(store){const db=await nkNoteDb();return nkNoteIdbRequest(db.transaction(store,'readonly').objectStore(store).getAll());}
  async function nkNoteIdbWrite(stores,work){
    const db=await nkNoteDb();
    return new Promise((resolve,reject)=>{
      const tx=db.transaction(stores,'readwrite');
      tx.oncomplete=()=>resolve(true);
      tx.onerror=()=>reject(tx.error||new Error('Note image storage failed.'));
      tx.onabort=()=>reject(tx.error||new Error('Note image storage was interrupted. The device may be out of space.'));
      work(name=>tx.objectStore(name));
    });
  }
  function nkNoteAssetSave(meta,variants){
    return nkNoteIdbWrite(NK_NOTE_STORES,store=>{
      store('meta').put(meta);
      ['full','preview','thumb'].forEach(name=>{if(variants[name])store(name).put({id:meta.id,mime:variants[name].mime,data:variants[name].data});});
    });
  }
  function nkNoteAssetDrop(id,keepMeta){
    nkNoteUrlForget(id);
    return nkNoteIdbWrite(NK_NOTE_STORES,store=>{
      ['full','preview','thumb'].forEach(name=>store(name).delete(String(id)));
      if(keepMeta)store('meta').put(keepMeta);else store('meta').delete(String(id));
    });
  }

  /* ---------- object URLs (bounded so decoded images do not pile up) ---------- */
  const nkNoteUrls=new Map();
  function nkNoteUrlForget(id){for(const key of [...nkNoteUrls.keys()])if(key.startsWith(id+'|')){URL.revokeObjectURL(nkNoteUrls.get(key));nkNoteUrls.delete(key);}}
  async function nkNoteAssetUrl(id,variant='preview'){
    const key=`${id}|${variant}`;
    if(nkNoteUrls.has(key)){const url=nkNoteUrls.get(key);nkNoteUrls.delete(key);nkNoteUrls.set(key,url);return url;}
    let record=await nkNoteIdbGet(variant,id);
    if(!record&&variant!=='full')record=await nkNoteIdbGet('full',id);
    if(!record?.data)return null;
    const url=URL.createObjectURL(new Blob([record.data],{type:record.mime||'image/jpeg'}));
    nkNoteUrls.set(key,url);
    while(nkNoteUrls.size>48){const [oldKey,oldUrl]=nkNoteUrls.entries().next().value;URL.revokeObjectURL(oldUrl);nkNoteUrls.delete(oldKey);}
    return url;
  }

  /* ---------- image processing ---------- */
  function nkNoteNewAssetId(){return `na_${Date.now().toString(36)}_${Math.random().toString(36).slice(2,12)}`;}
  function nkNoteCanvas(w,h){const canvas=document.createElement('canvas');canvas.width=w;canvas.height=h;return canvas;}
  function nkNoteCanvasBlob(canvas,type,quality){return new Promise(resolve=>canvas.toBlob(resolve,type,quality));}
  function nkNoteRelease(canvas){if(canvas){canvas.width=0;canvas.height=0;}}
  async function nkNoteDecode(blob){
    if(typeof createImageBitmap==='function'){
      try{const bitmap=await createImageBitmap(blob,{imageOrientation:'from-image'});return {source:bitmap,w:bitmap.width,h:bitmap.height,close:()=>bitmap.close?.()};}catch(_){}
    }
    const url=URL.createObjectURL(blob),img=new Image();
    img.decoding='async';img.src=url;
    try{await img.decode();}catch(_){URL.revokeObjectURL(url);throw new Error('This image format cannot be opened on this device. Export it as JPG or PNG.');}
    return {source:img,w:img.naturalWidth,h:img.naturalHeight,close:()=>URL.revokeObjectURL(url)};
  }
  // Draws onto white (transparent PNG exports stay readable) and lowers quality, then size, until it fits.
  async function nkNoteEncode(source,w,h,edge,qualities){
    let scale=Math.min(1,edge/Math.max(w,h),Math.sqrt(NK_NOTE_MAX_PIXELS/(w*h)));
    for(let attempt=0;attempt<6;attempt++){
      const cw=Math.max(1,Math.round(w*scale)),ch=Math.max(1,Math.round(h*scale)),canvas=nkNoteCanvas(cw,ch),ctx=canvas.getContext('2d');
      ctx.fillStyle='#fff';ctx.fillRect(0,0,cw,ch);ctx.imageSmoothingEnabled=true;ctx.imageSmoothingQuality='high';ctx.drawImage(source,0,0,cw,ch);
      for(const quality of qualities){
        const blob=await nkNoteCanvasBlob(canvas,'image/jpeg',quality);
        if(blob&&blob.size<=NK_NOTE_MAX_BYTES){nkNoteRelease(canvas);return {mime:'image/jpeg',data:await blob.arrayBuffer(),w:cw,h:ch};}
      }
      nkNoteRelease(canvas);scale*=0.8;
    }
    throw new Error('This image is too large to save.');
  }
  async function nkNoteVariants(source,w,h,original){
    const full=original||await nkNoteEncode(source,w,h,NK_NOTE_FULL_EDGE,[0.92,0.86,0.8]);
    const small=Math.max(w,h)<=NK_NOTE_PREVIEW_EDGE&&full.data.byteLength<=600000;
    const preview=small?null:await nkNoteEncode(source,w,h,NK_NOTE_PREVIEW_EDGE,[0.86,0.8]);
    const thumb=await nkNoteEncode(source,w,h,NK_NOTE_THUMB_EDGE,[0.8]);
    return {full,preview,thumb};
  }
  async function nkNoteStoreAsset(source,w,h,original,info){
    const variants=await nkNoteVariants(source,w,h,original);
    const id=nkNoteNewAssetId(),full=variants.full;
    const meta={id,mime:full.mime,w:full.w,h:full.h,bytes:full.data.byteLength,createdAt:Date.now(),draft:true,uploadedTo:'',deleted:false};
    await nkNoteAssetSave(meta,variants);
    return {type:'image',source:info.source,label:info.label,asset:{id,mime:meta.mime,w:meta.w,h:meta.h,bytes:meta.bytes}};
  }
  async function nkNoteImportImage(file){
    if(!file||!/^image\//.test(file.type||'')&&!/\.(jpe?g|png|webp|heic|heif|gif)$/i.test(file.name||''))throw new Error('Choose a JPG, PNG or screenshot image.');
    const decoded=await nkNoteDecode(file);
    try{
      if(!decoded.w||!decoded.h)throw new Error('This image is empty.');
      // Keep the exact original bytes when they already fit; small handwriting stays as sharp as exported.
      const keep=NK_NOTE_MIME.includes(file.type)&&file.size<=NK_NOTE_MAX_BYTES&&Math.max(decoded.w,decoded.h)<=NK_NOTE_FULL_EDGE&&decoded.w*decoded.h<=NK_NOTE_MAX_PIXELS;
      const original=keep?{mime:file.type,data:await file.arrayBuffer(),w:decoded.w,h:decoded.h}:null;
      return await nkNoteStoreAsset(decoded.source,decoded.w,decoded.h,original,{source:'image',label:String(file.name||'Image').replace(/\.[a-z0-9]+$/i,'').slice(0,80)||'Image'});
    }finally{decoded.close();}
  }

  /* ---------- PDF pages ---------- */
  // pdf.js 6 calls Map/WeakMap getOrInsertComputed, which older Safari and Android WebView lack.
  function nkNoteMapUpsertPolyfill(){
    [typeof Map==='function'&&Map,typeof WeakMap==='function'&&WeakMap].forEach(Type=>{
      if(!Type)return;const proto=Type.prototype;
      if(!proto.getOrInsert)Object.defineProperty(proto,'getOrInsert',{configurable:true,writable:true,value(key,value){if(!this.has(key))this.set(key,value);return this.get(key);}});
      if(!proto.getOrInsertComputed)Object.defineProperty(proto,'getOrInsertComputed',{configurable:true,writable:true,value(key,compute){if(!this.has(key))this.set(key,compute(key));return this.get(key);}});
    });
  }
  nkNoteMapUpsertPolyfill();
  let nkNotePdfjsPromise=null;
  function nkNotePdfjs(){
    if(!nkNotePdfjsPromise)nkNotePdfjsPromise=import('./vendor/pdfjs/pdf.min.mjs').then(pdfjs=>{if(!pdfjs.GlobalWorkerOptions.workerSrc)pdfjs.GlobalWorkerOptions.workerSrc='./vendor/pdfjs/pdf.worker.min.mjs';return pdfjs;});
    nkNotePdfjsPromise.catch(()=>{nkNotePdfjsPromise=null;});
    return nkNotePdfjsPromise;
  }
  async function nkNoteRenderPdfPage(doc,number,edge){
    const page=await doc.getPage(number),base=page.getViewport({scale:1});
    const scale=Math.min(edge/Math.max(base.width,base.height),Math.sqrt(NK_NOTE_MAX_PIXELS/(base.width*base.height)));
    const viewport=page.getViewport({scale}),canvas=nkNoteCanvas(Math.max(1,Math.floor(viewport.width)),Math.max(1,Math.floor(viewport.height)));
    const ctx=canvas.getContext('2d',{alpha:false});ctx.fillStyle='#fff';ctx.fillRect(0,0,canvas.width,canvas.height);
    await page.render({canvasContext:ctx,viewport}).promise;
    page.cleanup?.();
    return canvas;
  }
  async function nkNoteImportPdfPage(doc,number,name){
    const canvas=await nkNoteRenderPdfPage(doc,number,NK_NOTE_FULL_EDGE);
    try{return await nkNoteStoreAsset(canvas,canvas.width,canvas.height,null,{source:'pdf',label:`${name} · page ${number}`.slice(0,120)});}
    finally{nkNoteRelease(canvas);}
  }
  // Resolves to the page numbers the learner picked, or [] when the sheet is closed.
  function nkNotePdfPicker(doc,name,remaining){
    return new Promise(resolve=>{
      const limit=Math.min(NK_NOTE_PDF_IMPORT_LIMIT,remaining),chosen=new Set(),opener=document.activeElement;
      const sheet=document.createElement('div');
      sheet.className='nk-note-sheet';sheet.setAttribute('role','dialog');sheet.setAttribute('aria-modal','true');sheet.setAttribute('aria-label','Choose PDF pages');
      sheet.innerHTML=`<div class="nk-note-sheet-panel"><header><div><strong>Choose pages</strong><small>${esc(name)} · ${doc.numPages} page${doc.numPages===1?'':'s'} · up to ${limit}</small></div><button type="button" class="nk-note-sheet-close" aria-label="Close page picker">✕</button></header><div class="nk-note-pdf-grid">${Array.from({length:doc.numPages},(_,i)=>`<button type="button" class="nk-note-pdf-page" data-page="${i+1}" aria-pressed="false" aria-label="Page ${i+1}"><span class="nk-note-pdf-thumb"></span><span class="nk-note-pdf-label">Page ${i+1}</span></button>`).join('')}</div><footer><span role="status">Tap pages to add them</span><button type="button" class="nk-note-sheet-add" disabled>Add pages</button></footer></div>`;
      document.body.appendChild(sheet);
      const status=sheet.querySelector('[role="status"]'),add=sheet.querySelector('.nk-note-sheet-add');
      let closed=false,queue=Promise.resolve();
      const observer=typeof IntersectionObserver==='function'?new IntersectionObserver(entries=>entries.forEach(entry=>{if(entry.isIntersecting){observer.unobserve(entry.target);queueThumb(entry.target);}}),{root:sheet.querySelector('.nk-note-pdf-grid'),rootMargin:'200px'}):null;
      function queueThumb(button){
        queue=queue.then(async()=>{
          if(closed)return;
          const canvas=await nkNoteRenderPdfPage(doc,Number(button.dataset.page),260).catch(()=>null);
          if(!canvas||closed){nkNoteRelease(canvas);return;}
          canvas.className='nk-note-pdf-canvas';button.querySelector('.nk-note-pdf-thumb').replaceChildren(canvas);
        });
      }
      sheet.querySelectorAll('.nk-note-pdf-page').forEach((button,index)=>{if(observer)observer.observe(button);else if(index<24)queueThumb(button);});
      function finish(pages){
        if(closed)return;closed=true;observer?.disconnect();
        sheet.querySelectorAll('canvas').forEach(nkNoteRelease);sheet.remove();
        document.removeEventListener('keydown',onKey,true);opener?.focus?.({preventScroll:true});resolve(pages);
      }
      function onKey(event){if(event.key==='Escape'){event.preventDefault();event.stopPropagation();finish([]);}}
      document.addEventListener('keydown',onKey,true);
      sheet.querySelector('.nk-note-sheet-close').addEventListener('click',()=>finish([]));
      sheet.addEventListener('click',event=>{if(event.target===sheet)finish([]);});
      sheet.querySelector('.nk-note-pdf-grid').addEventListener('click',event=>{
        const button=event.target.closest('.nk-note-pdf-page');if(!button)return;
        const page=Number(button.dataset.page);
        if(chosen.has(page))chosen.delete(page);
        else if(chosen.size>=limit){status.textContent=`You can add up to ${limit} page${limit===1?'':'s'} here.`;return;}
        else chosen.add(page);
        button.setAttribute('aria-pressed',String(chosen.has(page)));
        status.textContent=chosen.size?`${chosen.size} of ${limit} selected`:'Tap pages to add them';
        add.disabled=!chosen.size;add.textContent=chosen.size?`Add ${chosen.size} page${chosen.size===1?'':'s'}`:'Add pages';
      });
      add.addEventListener('click',()=>finish([...chosen].sort((a,b)=>a-b)));
      sheet.querySelector('.nk-note-sheet-close').focus({preventScroll:true});
    });
  }
  async function nkNoteImportPdf(file,remaining,progress){
    if(remaining<=0)throw new Error(`A note holds up to ${NK_NOTE_MEDIA_LIMIT} images or pages.`);
    const pdfjs=await nkNotePdfjs();
    let doc;
    try{doc=await pdfjs.getDocument({data:new Uint8Array(await file.arrayBuffer()),isEvalSupported:false}).promise;}
    catch(error){throw new Error(/password/i.test(String(error?.name||error?.message||''))?'This PDF is password protected.':'This PDF could not be opened.');}
    const name=String(file.name||'PDF').replace(/\.pdf$/i,'').slice(0,60)||'PDF';
    try{
      const pages=doc.numPages===1?[1]:await nkNotePdfPicker(doc,name,remaining),blocks=[];
      for(const [index,number] of pages.entries()){
        progress?.(`Adding page ${index+1} of ${pages.length}…`);
        blocks.push(await nkNoteImportPdfPage(doc,number,name));
      }
      return blocks;
    }finally{doc.destroy?.();}
  }

  /* ---------- note lifecycle ---------- */
  function nkNoteSessionUid(){return typeof nkAuth!=='undefined'&&nkAuth?.uid?String(nkAuth.uid):'';}
  // Saved notes keep their assets; images removed from a saved note are deleted here and in the cloud.
  async function nkNoteAssetsCommit(keptIds,removedAssets){
    try{
      for(const id of keptIds){const meta=await nkNoteIdbGet('meta',id);if(meta?.draft)await nkNoteIdbWrite(['meta'],store=>store('meta').put({...meta,draft:false}));}
      const uid=nkNoteSessionUid();
      for(const asset of removedAssets){
        const id=String(asset.id),meta=await nkNoteIdbGet('meta',id);
        // Unknown locally means another device uploaded it to this account.
        const remote=uid&&(!meta||meta.uploadedTo===uid);
        await nkNoteAssetDrop(id,remote?{id,deleted:true,deleteFrom:uid,bytes:Number(meta?.bytes||asset.bytes||0),createdAt:Number(meta?.createdAt||Date.now())}:null);
      }
    }catch(_){}
    nkNoteAssetsSyncSoon();
  }
  function nkNoteReferencedAssets(){
    const out=new Map();
    Object.values(state.questionNotes||{}).forEach(note=>{if(note&&!note.deleted)nkNoteBlocks(note).forEach(block=>{if(block.type==='image')out.set(block.asset.id,block.asset);});});
    return out;
  }
  async function nkNoteCollectDrafts(){
    try{
      const referenced=nkNoteReferencedAssets(),cutoff=Date.now()-86400000;
      for(const meta of await nkNoteIdbAll('meta'))if(meta.draft&&!referenced.has(meta.id)&&Number(meta.createdAt||0)<cutoff)await nkNoteAssetDrop(meta.id,null);
    }catch(_){}
  }
  async function nkNoteAssetsForgetAccount(uid){
    try{for(const meta of await nkNoteIdbAll('meta'))if(!meta.deleted&&String(meta.uploadedTo||'')===String(uid||''))await nkNoteAssetDrop(meta.id,null);}catch(_){}
  }

  /* ---------- cloud transfer (one asset at a time, never inside the study-state envelope pull) ---------- */
  let nkNoteSyncBusy=false,nkNoteSyncTimer=null;
  const nkNoteMissing=new Map();
  function nkNoteAssetsSyncSoon(delay=1500){
    if(typeof nkAuth==='undefined'||!nkAuth)return;
    clearTimeout(nkNoteSyncTimer);nkNoteSyncTimer=setTimeout(()=>{nkNoteAssetsSync().catch(()=>{});},delay);
  }
  function nkNoteChunkCount(bytes){return Math.max(1,Math.ceil(Math.ceil(Number(bytes||0)/3)*4/NK_NOTE_CHUNK_CHARS));}
  function nkNoteChunkUrl(uid,id,index){return `${nkFirestoreRoot()}/users/${encodeURIComponent(uid)}/noteAssets/${encodeURIComponent(`${id}~${index}`)}`;}
  function nkNoteBase64(buffer){
    return new Promise((resolve,reject)=>{const reader=new FileReader();reader.onload=()=>resolve(String(reader.result).split(',')[1]||'');reader.onerror=()=>reject(reader.error);reader.readAsDataURL(new Blob([buffer]));});
  }
  async function nkNoteFromBase64(text,mime){return (await fetch(`data:${mime};base64,${text}`)).arrayBuffer();}
  async function nkNoteUpload(token,uid,meta){
    const full=await nkNoteIdbGet('full',meta.id);if(!full?.data)return;
    const encoded=await nkNoteBase64(full.data),count=Math.max(1,Math.ceil(encoded.length/NK_NOTE_CHUNK_CHARS));
    for(let index=0;index<count;index++){
      const payload=JSON.stringify({v:1,assetId:meta.id,index,count,mime:full.mime,bytes:full.data.byteLength,w:meta.w,h:meta.h,data:encoded.slice(index*NK_NOTE_CHUNK_CHARS,(index+1)*NK_NOTE_CHUNK_CHARS)});
      const envelope={kind:'noteAssets',entityId:`${meta.id}~${index}`,ownerDevice:nkSyncMeta.deviceId,updatedAt:Date.now(),deleted:false,payload,schemaVersion:1};
      await nkFetchJson(nkNoteChunkUrl(uid,meta.id,index),{method:'PATCH',headers:{Authorization:`Bearer ${token}`,'Content-Type':'application/json'},body:JSON.stringify(nkFirestoreDocument(envelope))});
    }
    const latest=await nkNoteIdbGet('meta',meta.id);
    // Removed from its note while uploading: clear the copy that just arrived.
    if(!latest||latest.deleted){await nkNoteRemoteDelete(token,uid,{id:meta.id,bytes:full.data.byteLength});return;}
    await nkNoteIdbWrite(['meta'],store=>store('meta').put({...latest,uploadedTo:uid}));
  }
  async function nkNoteRemoteDelete(token,uid,meta){
    for(let index=0;index<nkNoteChunkCount(meta.bytes);index++){
      const envelope={kind:'noteAssets',entityId:`${meta.id}~${index}`,ownerDevice:nkSyncMeta.deviceId,updatedAt:Date.now(),deleted:true,payload:'',schemaVersion:1};
      try{await nkFetchJson(`${nkNoteChunkUrl(uid,meta.id,index)}?currentDocument.exists=true`,{method:'PATCH',headers:{Authorization:`Bearer ${token}`,'Content-Type':'application/json'},body:JSON.stringify(nkFirestoreDocument(envelope))});}
      catch(error){if(error.status!==404&&error.status!==400&&!/NOT_FOUND|FAILED_PRECONDITION/.test(String(error.message)))throw error;}
    }
    await nkNoteIdbWrite(['meta'],store=>store('meta').delete(meta.id));
  }
  async function nkNoteDownload(token,uid,asset){
    const read=async index=>{
      try{const doc=await nkFetchJson(nkNoteChunkUrl(uid,asset.id,index),{headers:{Authorization:`Bearer ${token}`}}),envelope=nkDecodeDocument(doc);return envelope.deleted?null:nkJson(envelope.payload,null);}
      catch(error){if(error.status===404||/NOT_FOUND/.test(String(error.message)))return null;throw error;}
    };
    const first=await read(0);if(!first||first.assetId!==asset.id)return false;
    const parts=[first.data];
    for(let index=1;index<Number(first.count||1);index++){const part=await read(index);if(!part)return false;parts.push(part.data);}
    const mime=NK_NOTE_MIME.includes(first.mime)?first.mime:'image/jpeg',data=await nkNoteFromBase64(parts.join(''),mime);
    if(Number(first.bytes)&&data.byteLength!==Number(first.bytes))return false;
    const decoded=await nkNoteDecode(new Blob([data],{type:mime}));
    try{
      const variants=await nkNoteVariants(decoded.source,decoded.w,decoded.h,{mime,data,w:decoded.w,h:decoded.h});
      await nkNoteAssetSave({id:asset.id,mime,w:decoded.w,h:decoded.h,bytes:data.byteLength,createdAt:Date.now(),draft:false,uploadedTo:uid,deleted:false},variants);
    }finally{decoded.close();}
    return true;
  }
  async function nkNoteAssetsSync(){
    if(nkNoteSyncBusy||typeof nkAuth==='undefined'||!nkAuth||!navigator.onLine)return;
    if((typeof nkCloudResetting!=='undefined'&&nkCloudResetting)||(typeof nkCloudBusy!=='undefined'&&nkCloudBusy)){nkNoteAssetsSyncSoon(4000);return;}
    nkNoteSyncBusy=true;let more=false;
    try{
      const token=await nkRefreshAuth();await nkResolveFirebaseProjectId();
      const uid=String(nkAuth.uid),referenced=nkNoteReferencedAssets(),metas=new Map((await nkNoteIdbAll('meta')).map(meta=>[meta.id,meta]));
      let budget=6;
      for(const meta of metas.values()){
        if(!meta.deleted||budget<=0)continue;
        if(meta.deleteFrom!==uid){if(!meta.deleteFrom)await nkNoteIdbWrite(['meta'],store=>store('meta').delete(meta.id));continue;}
        await nkNoteRemoteDelete(token,uid,meta);budget--;
      }
      for(const [id,asset] of referenced){
        if(budget<=0){more=true;break;}
        const meta=metas.get(id);
        if(meta&&!meta.deleted){if(meta.uploadedTo!==uid){await nkNoteUpload(token,uid,meta);budget--;}continue;}
        if(meta?.deleted)continue;
        const retryAt=nkNoteMissing.get(id)||0;if(retryAt>Date.now())continue;
        if(await nkNoteDownload(token,uid,asset)){nkNoteMissing.delete(id);document.dispatchEvent(new CustomEvent('nk-note-asset-ready',{detail:{id}}));}
        else nkNoteMissing.set(id,Date.now()+120000);
        budget--;
        await new Promise(resolve=>setTimeout(resolve,30));
      }
    }catch(_){
      // Study sync keeps its own status; images simply retry later.
      more=false;nkNoteAssetsSyncSoon(60000);
    }finally{nkNoteSyncBusy=false;}
    if(more)nkNoteAssetsSyncSoon(800);
  }

  /* ---------- display ---------- */
  function nkNoteMediaFrame(block,variant,index){
    const a=block.asset,label=block.label||(block.source==='pdf'?'PDF page':'Image');
    return `<span class="nk-note-media-frame" style="aspect-ratio:${a.w}/${a.h}"><img alt="${esc(label)}" width="${a.w}" height="${a.h}" decoding="async" data-nk-note-asset="${esc(a.id)}" data-nk-note-variant="${variant}"${index==null?'':` data-nk-note-index="${index}"`}><span class="nk-note-media-missing">${typeof nkAuth!=='undefined'&&nkAuth?'Image will appear after it syncs to this device.':'Image is not on this device. Sign in to sync it.'}</span></span>`;
  }
  function nkNoteHydrate(root){
    if(!root?.querySelectorAll)return;
    root.querySelectorAll('img[data-nk-note-asset]:not([src])').forEach(img=>{
      if(img.dataset.nkNotePending)return;img.dataset.nkNotePending='1';
      nkNoteAssetUrl(img.dataset.nkNoteAsset,img.dataset.nkNoteVariant||'preview').then(url=>{
        delete img.dataset.nkNotePending;const frame=img.closest('.nk-note-media-frame');
        if(url){
          frame?.classList.remove('is-missing');
          // The frame shimmers until the picture is decoded, then the image fades in.
          const shown=()=>frame?.classList.add('is-loaded');
          img.addEventListener('load',shown,{once:true});img.src=url;
          if(img.complete&&img.naturalWidth)shown();
        }
        else{frame?.classList.add('is-missing');nkNoteAssetsSyncSoon(300);}
      }).catch(()=>{delete img.dataset.nkNotePending;img.closest('.nk-note-media-frame')?.classList.add('is-missing');});
    });
  }
  if(typeof document!=='undefined'&&document.addEventListener)document.addEventListener('nk-note-asset-ready',event=>{
    const id=String(event.detail?.id||'');
    document.querySelectorAll('img[data-nk-note-asset]').forEach(img=>{if(img.dataset.nkNoteAsset===id&&!img.getAttribute('src'))nkNoteHydrate(img.parentElement);});
  });

  // Full-screen viewer with pinch, drag, double-tap and button zoom (the app viewport disables browser zoom).
  function nkNoteOpenViewer(blocks,start){
    const media=blocks.filter(block=>block.type==='image');if(!media.length)return;
    const opener=document.activeElement,viewer=document.createElement('div');
    let index=Math.max(0,Math.min(media.length-1,Number(start)||0)),scale=1,tx=0,ty=0,lastTap=0;
    const pointers=new Map();let pinch=null,drag=null;
    viewer.className='nk-note-viewer';viewer.setAttribute('role','dialog');viewer.setAttribute('aria-modal','true');viewer.setAttribute('aria-label','Note image');
    viewer.innerHTML=`<div class="nk-note-viewer-bar"><span class="nk-note-viewer-count" aria-live="polite"></span><div><button type="button" data-act="out" aria-label="Zoom out">−</button><button type="button" data-act="in" aria-label="Zoom in">+</button><button type="button" data-act="close" aria-label="Close image">✕</button></div></div><div class="nk-note-viewer-stage"><img alt="" draggable="false"></div>${media.length>1?'<button type="button" class="nk-note-viewer-nav is-prev" data-act="prev" aria-label="Previous image">‹</button><button type="button" class="nk-note-viewer-nav is-next" data-act="next" aria-label="Next image">›</button>':''}`;
    document.body.appendChild(viewer);
    const stage=viewer.querySelector('.nk-note-viewer-stage'),img=stage.querySelector('img'),count=viewer.querySelector('.nk-note-viewer-count');
    const apply=()=>{img.style.transform=`translate(${tx}px,${ty}px) scale(${scale})`;};
    const clamp=()=>{const r=stage.getBoundingClientRect();if(scale<=1){scale=1;tx=0;ty=0;return;}tx=Math.min(0,Math.max(r.width-r.width*scale,tx));ty=Math.min(0,Math.max(r.height-r.height*scale,ty));};
    const zoomAt=(next,x,y)=>{next=Math.max(1,Math.min(8,next));tx=x-(x-tx)*(next/scale);ty=y-(y-ty)*(next/scale);scale=next;clamp();apply();};
    const centre=()=>{const r=stage.getBoundingClientRect();return [r.width/2,r.height/2];};
    async function show(){
      scale=1;tx=0;ty=0;apply();img.removeAttribute('src');
      const block=media[index];img.alt=block.label||'Note image';count.textContent=media.length>1?`${index+1} / ${media.length}`:(block.label||'');
      const url=await nkNoteAssetUrl(block.asset.id,'full').catch(()=>null)||await nkNoteAssetUrl(block.asset.id,'preview').catch(()=>null);
      if(media[index]===block&&url)img.src=url;
    }
    function close(){document.removeEventListener('keydown',onKey,true);viewer.remove();opener?.focus?.({preventScroll:true});}
    function onKey(event){
      // The question screen underneath also listens for arrows; the open viewer owns them.
      if(!['Escape','ArrowRight','ArrowLeft'].includes(event.key))return;
      event.preventDefault();event.stopPropagation();
      if(event.key==='Escape')close();
      else if(media.length>1){index=(index+(event.key==='ArrowRight'?1:media.length-1))%media.length;show();}
    }
    document.addEventListener('keydown',onKey,true);
    viewer.addEventListener('click',event=>{
      const act=event.target.closest('[data-act]')?.dataset.act;if(!act)return;
      if(act==='close')close();
      else if(act==='in')zoomAt(scale*1.6,...centre());
      else if(act==='out')zoomAt(scale/1.6,...centre());
      else if(act==='next'){index=(index+1)%media.length;show();}
      else if(act==='prev'){index=(index-1+media.length)%media.length;show();}
    });
    const local=(x,y)=>{const r=stage.getBoundingClientRect();return [x-r.left,y-r.top];};
    let tap=null;
    stage.addEventListener('pointerdown',event=>{
      stage.setPointerCapture?.(event.pointerId);pointers.set(event.pointerId,[event.clientX,event.clientY]);
      if(pointers.size===2){const [a,b]=[...pointers.values()];pinch={distance:Math.hypot(a[0]-b[0],a[1]-b[1])||1,scale};drag=null;tap=null;}
      else if(pointers.size===1){drag={x:event.clientX,y:event.clientY,tx,ty};tap={x:event.clientX,y:event.clientY};}
    });
    stage.addEventListener('pointermove',event=>{
      if(!pointers.has(event.pointerId))return;pointers.set(event.pointerId,[event.clientX,event.clientY]);
      if(tap&&Math.hypot(event.clientX-tap.x,event.clientY-tap.y)>8)tap=null;
      if(pinch&&pointers.size>=2){const [a,b]=[...pointers.values()];zoomAt(pinch.scale*(Math.hypot(a[0]-b[0],a[1]-b[1])/pinch.distance),...local((a[0]+b[0])/2,(a[1]+b[1])/2));}
      else if(drag&&scale>1){tx=drag.tx+event.clientX-drag.x;ty=drag.ty+event.clientY-drag.y;clamp();apply();}
    });
    const end=event=>{
      if(!pointers.has(event.pointerId))return;
      pointers.delete(event.pointerId);
      if(pointers.size<2)pinch=null;
      if(pointers.size===1){const [rest]=pointers.values();drag={x:rest[0],y:rest[1],tx,ty};}
      if(event.type==='pointerup'&&!pointers.size&&tap){
        const now=Date.now();
        if(now-lastTap<320){zoomAt(scale>1?1:2.5,...local(event.clientX,event.clientY));lastTap=0;}else lastTap=now;
      }
      if(!pointers.size){drag=null;tap=null;}
    };
    stage.addEventListener('pointerup',end);stage.addEventListener('pointercancel',end);
    stage.addEventListener('wheel',event=>{event.preventDefault();zoomAt(scale*(event.deltaY<0?1.15:1/1.15),...local(event.clientX,event.clientY));},{passive:false});
    viewer.querySelector('[data-act="close"]').focus({preventScroll:true});
    show();
  }

  function nkNoteMediaStartup(){
    if(typeof window==='undefined'||typeof indexedDB==='undefined')return;
    setTimeout(()=>{nkNoteCollectDrafts();},30000);
    window.addEventListener('online',()=>nkNoteAssetsSyncSoon(2000));
  }
  nkNoteMediaStartup();
  /* NK_NOTE_MEDIA_V1_END */
