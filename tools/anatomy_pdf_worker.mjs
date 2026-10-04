/* Same-origin streaming bridge for the configured, unchanged Anatomy source. */
const SOURCE_URL=__ANATOMY_SOURCE_URL__;
const ROBOTS_DIRECTIVES='noindex, nofollow, noarchive, nosnippet, noimageindex';
const SECURITY_HEADERS=__WEB_SECURITY_HEADERS__;
function excludeFromSearch(response) {
  const headers=new Headers(response.headers);
  headers.set('X-Robots-Tag',ROBOTS_DIRECTIVES);
  for(const [name,value] of Object.entries(SECURITY_HEADERS))headers.set(name,value);
  return new Response(response.body,{status:response.status,statusText:response.statusText,headers});
}
export default {
  async fetch(request,env) {
    if(new URL(request.url).pathname!=='/anatomy-source.pdf')return excludeFromSearch(await env.ASSETS.fetch(request));
    if(!['GET','HEAD'].includes(request.method))return excludeFromSearch(new Response('Method not allowed',{status:405,headers:{Allow:'GET, HEAD'}}));
    const headers=new Headers();
    for(const key of ['Range','If-Range','If-None-Match','If-Modified-Since'])if(request.headers.has(key))headers.set(key,request.headers.get(key));
    try {
      const upstream=await fetch(SOURCE_URL,{method:request.method,headers});
      const out=new Headers(upstream.headers);
      out.set('Content-Type','application/pdf');out.set('X-Content-Type-Options','nosniff');
      // Streaming preserves byte ranges and avoids buffering the 46 MB PDF.
      return excludeFromSearch(new Response(upstream.body,{status:upstream.status,headers:out}));
    } catch {return excludeFromSearch(new Response('Source PDF temporarily unavailable',{status:502}));}
  }
};
