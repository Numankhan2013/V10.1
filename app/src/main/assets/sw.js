/* NK QBank PWA service worker. BUILD_VERSION is replaced in the web artifact. */
const BUILD_VERSION='dev';
const SHELL_CACHE=`nk-qbank-shell-${BUILD_VERSION}`;
const RUNTIME_CACHE=`nk-qbank-runtime-${BUILD_VERSION}`;
// Content-hashed figures live in one unversioned cache that survives deploys.
// They are filled in the background so installation never waits on ~600 MB.
const MEDIA_CACHE='nk-qbank-media';
const SHELL=['./app.css','./redesign/nk-pdf-loader.js','./redesign/nk-viewer.js','./pdf_glyph_repairs.json','./redesign/nk-feel.js','./redesign/vendor/motion-12.23.12.min.js','./redesign/nk-icons.js','./redesign/nk-redesign.js','./redesign/fonts/Geist-Variable.woff2','./redesign/fonts/GeistMono-Variable.woff2','./vendor/ts-fsrs/ts-fsrs-5.4.2.umd.js','./vendor/ts-fsrs/LICENSE','./','./index.html','./manifest.webmanifest','./qbank-config.js','./nk-store.js','./qbank-icon-192.png','./qbank-icon-512.png','./nk-icon-maskable-192.png','./nk-icon-maskable-512.png','./apple-touch-icon.png','./nk-icon.svg','./favicon-32.png','./subjects_qbank_data.js','./qbank_data.js','./source_visual_metadata.js','./source_visual_renderer.js','./biochemistry_source_solution_map.js','./subject_source_solution_maps.js','./physiology_image_pages.js','./web_pdf_renderer.mjs','./vendor/pdfjs/pdf.min.mjs','./vendor/pdfjs/pdf.worker.min.mjs'];
const MEDIA=[];
self.addEventListener('install',event=>event.waitUntil(caches.open(SHELL_CACHE).then(cache=>cache.addAll(SHELL))));
self.addEventListener('activate',event=>event.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(key=>key.startsWith('nk-qbank-')&&key!==MEDIA_CACHE&&!key.endsWith(BUILD_VERSION)).map(key=>caches.delete(key)))).then(()=>self.clients.claim())));
function isCloud(url){return /(?:^|\.)(?:googleapis\.com|firebaseio\.com)$/.test(url.hostname);}
let mediaPaths=null;
function mediaUrl(path){return new URL(path,self.registration.scope).href;}
function isMedia(url){if(!mediaPaths)mediaPaths=new Set(MEDIA.map(mediaUrl));return mediaPaths.has(url.href.split('#')[0]);}
async function tell(data){for(const client of await self.clients.matchAll({includeUncontrolled:true}))client.postMessage(data);}
let mediaRun=null;
function syncMedia(){
  // Resumable: each run fetches only what is missing, tolerates failures and
  // prunes figures that are no longer part of the current build.
  if(mediaRun)return mediaRun;
  mediaRun=(async()=>{
    const cache=await caches.open(MEDIA_CACHE);
    const wanted=new Set(MEDIA.map(mediaUrl));
    const have=new Set();
    for(const request of await cache.keys()){if(wanted.has(request.url))have.add(request.url);else await cache.delete(request);}
    const missing=[...wanted].filter(url=>!have.has(url));
    let done=wanted.size-missing.length,failed=0,next=0;
    void tell({type:'NK_MEDIA_PROGRESS',done,total:wanted.size,failed});
    const worker=async()=>{
      while(next<missing.length){
        const url=missing[next++];
        try{const response=await fetch(url);if(response.ok)await cache.put(url,response);else failed++;}catch{failed++;}
        done++;
        if(done%25===0)void tell({type:'NK_MEDIA_PROGRESS',done,total:wanted.size,failed});
      }
    };
    await Promise.all(Array.from({length:4},worker));
    void tell({type:'NK_MEDIA_PROGRESS',done,total:wanted.size,failed,complete:true});
  })().finally(()=>{mediaRun=null;});
  return mediaRun;
}
self.addEventListener('fetch',event=>{
  if(event.request.method!=='GET')return;
  const url=new URL(event.request.url);if(isCloud(url))return;
  if(event.request.mode==='navigate'){
    event.respondWith(fetch(event.request).then(response=>{const scope=new URL(self.registration.scope).pathname,path=url.pathname;const appShell=path===scope||path===scope+'index.html';if(response.ok&&appShell&&/text\/html/.test(response.headers.get('content-type')||'')){const copy=response.clone();caches.open(SHELL_CACHE).then(cache=>cache.put('./index.html',copy));}return response;}).catch(()=>caches.match('./index.html')));return;
  }
  if(url.origin!==self.location.origin)return;
  event.respondWith(caches.match(event.request).then(cached=>cached||fetch(event.request).then(response=>{if(response.ok){const copy=response.clone();caches.open(isMedia(url)?MEDIA_CACHE:RUNTIME_CACHE).then(cache=>cache.put(event.request,copy));}return response;})));
});
self.addEventListener('message',event=>{
  if(event.data==='SKIP_WAITING')self.skipWaiting();
  if(event.data?.type==='NK_QBANK_VERSION')event.ports?.[0]?.postMessage({version:BUILD_VERSION});
  if(event.data?.type==='NK_MEDIA_SYNC')event.waitUntil(syncMedia());
});
