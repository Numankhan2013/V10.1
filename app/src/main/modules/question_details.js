/* NK_QUESTION_DETAILS_V1_START */
  // The web build moves explanation fields into per-subject packs fetched on
  // demand (tools/build_web_dist.py DetailPacks) and marks each question with
  // its pack. Questions without a mark (and local, unsplit builds) carry them inline.
  const nkDetailPacks=new Map();
  function nkDetailsReady(q){return !q||!Number.isInteger(q.detailPack);}
  function nkDetailPack(index){
    const files=Array.isArray(window.NK_DETAIL_PACKS)?window.NK_DETAIL_PACKS:[];
    if(!files[index])return Promise.reject(new Error('Unknown explanation pack'));
    if(!nkDetailPacks.has(index)){
      const load=fetch(files[index]).then(response=>{if(!response.ok)throw new Error(`HTTP ${response.status}`);return response.json();});
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
  function nkDetailsPending(q){
    const id=String(q.id);
    if(!nkDetailsWaiting.has(id)){
      nkDetailsWaiting.add(id);
      nkLoadDetails(q).then(()=>{
        nkDetailsWaiting.delete(id);
        if(document.querySelector(`[data-nk-details-pending="${CSS.escape(id)}"]`))render();
      },()=>{
        nkDetailsWaiting.delete(id);
        document.querySelectorAll(`[data-nk-details-pending="${CSS.escape(id)}"] .nk-source-empty`).forEach(el=>{el.textContent='The explanation could not be downloaded. Reopen this question when you are online.';});
      });
    }
    return `<div class="nk-study-support" data-nk-details-pending="${esc(id)}"><section class="nk-source-section"><header><div>${navIcon('book',19)}<strong>Explanation</strong></div></header><div class="nk-source-empty" role="status">Loading explanation…</div></section></div>`;
  }
/* NK_QUESTION_DETAILS_V1_END */
