/* NK_QUESTION_DETAILS_V1_START */
  // The web build moves explanation fields into per-subject packs fetched on
  // demand (tools/build_web_dist.py DetailPacks) and marks each question with
  // its pack. Questions without a mark (and local, unsplit builds) carry them inline.
  const nkDetailPacks=new Map();
  // A pack can be 12 MB, so a slow download is fine; one that stops receiving
  // bytes for 25 s is abandoned so the screen shows its retry message.
  function nkFetchJsonUnlessStalled(url,stallMs=25000){
    const control=typeof AbortController==='function'?new AbortController():null;
    let timer=0;
    const arm=()=>{clearTimeout(timer);if(control)timer=setTimeout(()=>control.abort(),stallMs);};
    arm();
    return fetch(url,control?{signal:control.signal}:undefined).then(response=>{
      if(!response.ok)throw new Error(`HTTP ${response.status}`);
      if(!response.body?.getReader){arm();return response.json();}
      const reader=response.body.getReader(),parts=[];
      const pump=()=>reader.read().then(({done,value})=>{
        if(done)return new Blob(parts).text().then(JSON.parse);
        parts.push(value);arm();return pump();
      });
      return pump();
    }).finally(()=>clearTimeout(timer));
  }
  function nkDetailsReady(q){return !q||!Number.isInteger(q.detailPack);}
  function nkDetailPack(index){
    const files=Array.isArray(window.NK_DETAIL_PACKS)?window.NK_DETAIL_PACKS:[];
    if(!files[index])return Promise.reject(new Error('Unknown explanation pack'));
    if(!nkDetailPacks.has(index)){
      const load=nkFetchJsonUnlessStalled(files[index]);
      // A failed download is retried by the next screen that needs it.
      nkDetailPacks.set(index,load.catch(error=>{nkDetailPacks.delete(index);throw error;}));
    }
    return nkDetailPacks.get(index);
  }
  function nkApplyDetails(q,pack){
    if(nkDetailsReady(q))return;
    const id=String(q.id),fields=pack?.q?.[id];
    if(fields){
      // Each copy of a question gets its own fields; sanitizing mutates them.
      const copy=JSON.parse(JSON.stringify(fields));
      if(id.startsWith('marrow__')){
        const clean=nkSanitizeMarrowQuestion({id,question:q.question,...copy});
        delete clean.id;delete clean.question;Object.assign(copy,clean);
      }
      Object.assign(q,copy);
    }
    if(pack?.gold?.[id]&&typeof NK_MARROW_EXPLANATION_GOLD_V1!=='undefined')NK_MARROW_EXPLANATION_GOLD_V1[id]=pack.gold[id];
    delete q.detailPack;
  }
  function nkLoadDetails(q){
    if(nkDetailsReady(q))return Promise.resolve(q);
    return nkDetailPack(q.detailPack).then(pack=>{
      const shared=BY_ID[String(q.id)];
      nkApplyDetails(q,pack);if(shared&&shared!==q)nkApplyDetails(shared,pack);
      return q;
    });
  }
  // Screens that may reveal an answer start the download while the question is read.
  function nkPrefetchDetails(q){if(!nkDetailsReady(q))nkLoadDetails(q).catch(()=>{});}
  const nkDetailsWaiting=new Set();
  // Screens that can swap the placeholder in place override this.
  let nkDetailsArrived=id=>{if(document.querySelector(`[data-nk-details-pending="${CSS.escape(id)}"]`))render();};
  function nkDetailsPending(q){
    const id=String(q.id);
    if(!nkDetailsWaiting.has(id)){
      nkDetailsWaiting.add(id);
      nkLoadDetails(q).then(()=>{
        nkDetailsWaiting.delete(id);
        nkDetailsArrived(id);
      },()=>{
        nkDetailsWaiting.delete(id);
        const retry=()=>{if(document.querySelector(`[data-nk-details-pending="${CSS.escape(id)}"]`)&&!nkDetailsWaiting.has(id)){document.querySelectorAll(`[data-nk-details-pending="${CSS.escape(id)}"] .nk-source-empty`).forEach(el=>{el.textContent='Loading explanation…';});nkDetailsPending(q);}};
        document.querySelectorAll(`[data-nk-details-pending="${CSS.escape(id)}"] .nk-source-empty`).forEach(el=>{
          el.innerHTML='<span>The explanation could not be loaded.</span> <button type="button" class="nk-details-retry">Try again</button>';
          el.querySelector('button').addEventListener('click',retry);
        });
        window.addEventListener('online',retry,{once:true});
      });
    }
    return `<div class="nk-study-support" data-nk-details-pending="${esc(id)}"><section class="nk-source-section"><header><div>${navIcon('book',19)}<strong>Explanation</strong></div></header><div class="nk-source-empty" role="status">Loading explanation…</div></section></div>`;
  }
/* NK_QUESTION_DETAILS_V1_END */
