/* NK_PWA_UPDATE_V2_START */
if ('serviceWorker' in navigator && location.hostname !== 'qbank.local') {
  window.addEventListener('load', async () => {
    try {
      let updateRequested=false,refreshing=false,pending=null;
      const currentVersion=document.querySelector('meta[name="nk-qbank-build"]')?.content;
      navigator.serviceWorker.addEventListener('controllerchange',()=>{
        if(updateRequested&&!refreshing){refreshing=true;location.reload();}
      });
      const registration=await navigator.serviceWorker.register('./sw.js');
      const versionOf=worker=>new Promise(resolve=>{
        const channel=new MessageChannel();
        const finish=value=>{clearTimeout(timer);channel.port1.close();resolve(value);};
        const timer=setTimeout(()=>finish(null),2000);
        channel.port1.onmessage=event=>finish(event.data?.version||null);
        try{worker.postMessage({type:'NK_QBANK_VERSION'},[channel.port2]);}catch{finish(null);}
      });
      const offer=async worker=>{
        if(!worker)return;
        const version=await versionOf(worker);
        // Network-first navigation can already be running the waiting build.
        // A waiting worker alone is not evidence that this page needs an update.
        if(!version||version===currentVersion||registration.waiting!==worker)return;
        try{if(sessionStorage.getItem('nk-pwa-dismissed')===version)return;}catch{}
        const session=window.QB?.getState()?.activeSession;
        if(['practice','exam'].includes(session?.mode)&&session.lifecycle!=='paused'){pending=worker;return;}
        if(document.querySelector('.nk-pwa-update'))return;
        const bar=document.createElement('div');bar.className='nk-pwa-update';bar.setAttribute('role','status');
        bar.innerHTML='<span>A QBank update is ready.</span><button type="button" class="nk-pwa-apply">Update</button><button type="button" class="nk-pwa-later" aria-label="Dismiss update for now">Later</button>';
        bar.querySelector('.nk-pwa-apply').onclick=()=>{updateRequested=true;worker.postMessage('SKIP_WAITING');};
        bar.querySelector('.nk-pwa-later').onclick=()=>{try{sessionStorage.setItem('nk-pwa-dismissed',version);}catch{}bar.remove();};
        document.body.appendChild(bar);
      };
      window.addEventListener('hashchange',()=>{if(pending){const worker=pending;pending=null;void offer(worker);}});
      if(registration.waiting)void offer(registration.waiting);
      registration.addEventListener('updatefound',()=>{
        const worker=registration.installing;
        worker?.addEventListener('statechange',()=>{
          if(worker.state==='installed'&&navigator.serviceWorker.controller)void offer(worker);
        });
      });
    }catch(error){console.warn('PWA update check unavailable',error);}
  });
}
/* NK_PWA_UPDATE_V2_END */
