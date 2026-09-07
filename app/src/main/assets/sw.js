/* NK QBank PWA service worker. BUILD_VERSION is replaced in the web artifact. */
const BUILD_VERSION='dev';
const SHELL_CACHE=`nk-qbank-shell-${BUILD_VERSION}`;
const RUNTIME_CACHE=`nk-qbank-runtime-${BUILD_VERSION}`;
const SHELL=['./','./index.html','./manifest.webmanifest','./qbank-config.js','./qbank-icon-192.png','./qbank-icon-512.png','./subjects_qbank_data.js','./qbank_data.js','./source_visual_metadata.js','./source_visual_renderer.js'];
self.addEventListener('install',event=>event.waitUntil(caches.open(SHELL_CACHE).then(cache=>cache.addAll(SHELL)).then(()=>self.skipWaiting())));
self.addEventListener('activate',event=>event.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(key=>key.startsWith('nk-qbank-')&&!key.endsWith(BUILD_VERSION)).map(key=>caches.delete(key)))).then(()=>self.clients.claim())));
function isCloud(url){return /(?:googleapis\.com|firebaseio\.com|securetoken\.googleapis\.com)$/.test(url.hostname);}
self.addEventListener('fetch',event=>{
  if(event.request.method!=='GET')return;
  const url=new URL(event.request.url);if(isCloud(url))return;
  if(event.request.mode==='navigate'){
    event.respondWith(fetch(event.request).then(response=>{const copy=response.clone();caches.open(SHELL_CACHE).then(cache=>cache.put('./index.html',copy));return response;}).catch(()=>caches.match('./index.html')));return;
  }
  if(url.origin!==self.location.origin)return;
  event.respondWith(caches.match(event.request).then(cached=>cached||fetch(event.request).then(response=>{if(response.ok){const copy=response.clone();caches.open(RUNTIME_CACHE).then(cache=>cache.put(event.request,copy));}return response;})));
});
self.addEventListener('message',event=>{if(event.data==='SKIP_WAITING')self.skipWaiting();});
