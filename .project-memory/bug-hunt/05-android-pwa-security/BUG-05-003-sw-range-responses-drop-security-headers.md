# BUG-05-003 — Service-worker PDF range responses drop the security headers

- **Area:** 05 android-pwa-security
- **Severity:** medium
- **Confidence:** high
- **Status:** fix applied — commit pending (this commit)
- **Files:** `app/src/main/assets/sw.js:72-83`
- **Introduced by:** cdd9cc7f (quota-abuse hardening)

## What happens

When a cached full PDF answers a byte-range request, `rangeResponse` builds a brand-new `Response` and copies only six transport headers (`Content-Length`, `Content-Range`, `Accept-Ranges`, `ETag`, `Last-Modified`, `Cache-Control`). Everything else from the cached response — `Content-Security-Policy`, `X-Frame-Options`, `X-Content-Type-Options`, `Referrer-Policy`, HSTS and the rest of the policy — is dropped. PDF byte ranges served by the service worker therefore ship without the security headers that the same file gets when served directly, so the two code paths disagree and the offline path is the weaker one.

## Evidence

`app/src/main/assets/sw.js:72-83`:

```javascript
async function rangeResponse(request){
  const cached=await caches.match(request.url);
  const m=/^bytes=(\d*)-(\d*)$/.exec(request.headers.get('range')||'');
  if(!cached||cached.status!==200||!m||(!m[1]&&!m[2]))return fetch(request);
  const blob=await cached.blob(),size=blob.size;
  const start=m[1]?Number(m[1]):Math.max(0,size-Number(m[2]));
  const end=m[1]&&m[2]?Math.min(Number(m[2]),size-1):size-1;
  if(start>end)return new Response(null,{status:416,headers:{'Content-Range':`bytes */${size}`}});
  return new Response(blob.slice(start,end+1),{status:206,headers:{
    'Content-Type':cached.headers.get('content-type')||'application/octet-stream',
    'Content-Range':`bytes ${start}-${end}/${size}`,'Content-Length':String(end-start+1),'Accept-Ranges':'bytes'}});
}
```

Only `Content-Type`, `Content-Range`, `Content-Length` and `Accept-Ranges` are set; the cached response's other headers are ignored.

## Learner impact

Security-header inconsistency on the offline/PWA path: cached PDF ranges lack the frame and MIME protections that the hosted response carries. No data loss, but the protected-headers contract is weaker offline.

## Root cause

`rangeResponse` reconstructs the response headers from a hard-coded allow-list instead of starting from the cached response's headers and overriding only the range-specific ones.

## Proposed fix

```diff
--- a/app/src/main/assets/sw.js
+++ b/app/src/main/assets/sw.js
@@ -77,9 +77,12 @@
   const start=m[1]?Number(m[1]):Math.max(0,size-Number(m[2]));
   const end=m[1]&&m[2]?Math.min(Number(m[2]),size-1):size-1;
   if(start>end)return new Response(null,{status:416,headers:{'Content-Range':`bytes */${size}`}});
-  return new Response(blob.slice(start,end+1),{status:206,headers:{
-    'Content-Type':cached.headers.get('content-type')||'application/octet-stream',
-    'Content-Range':`bytes ${start}-${end}/${size}`,'Content-Length':String(end-start+1),'Accept-Ranges':'bytes'}});
+  const headers=new Headers(cached.headers);
+  headers.set('Content-Type',cached.headers.get('content-type')||'application/octet-stream');
+  headers.set('Content-Range',`bytes ${start}-${end}/${size}`);
+  headers.set('Content-Length',String(end-start+1));
+  headers.set('Accept-Ranges','bytes');
+  return new Response(blob.slice(start,end+1),{status:206,statusText:'Partial Content',headers});
 }
 self.addEventListener('fetch',event=>{
   if(event.request.method!=='GET')return;
```

## Verification

- Inspect a cached PDF range response in DevTools: it should carry the same `Content-Security-Policy`, `X-Frame-Options`, `X-Content-Type-Options` and `Referrer-Policy` as the hosted file.
- Regressions to re-check: PDF.js byte-range loading, offline PDF viewing, Anatomy source PDF streaming.

## Alternatives considered

Keeping a hard-coded header list and adding the missing security headers by name would work, but starting from the cached headers is smaller and stays correct if the policy gains new headers later.

## Main-agent review

- **Verdict:** approved
- **Checked evidence:** yes
- **Checked patch:** yes
- **Notes:** Verified sw.js: the rangeResponse helper builds its own Response with only Content-Type/Content-Range/Content-Length/Accept-Ranges, dropping the security headers the origin serves. Medium severity, high confidence: the dropped headers are the ones _headers defines for the affected paths. Approved.


The finding is correct and the patch is right: the range responder rebuilt the headers from a hard-coded list instead of starting from the cached response's headers.

`tools/test_android_shell_contract_v1.py` is new and drives the shipped `rangeResponse` from `sw.js` for real, against a cached PDF that carries the hosted response's security headers, and asserts that the content security policy, the MIME protection, the frame protection and the referrer policy all survive the range response. On the pre-fix service worker the assertion fails with "the cached CSP must survive".
