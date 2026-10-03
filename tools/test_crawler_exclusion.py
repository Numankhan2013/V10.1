#!/usr/bin/env python3
"""Exercise Pages search exclusion without reading or changing source content."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
DIRECTIVES = "noindex, nofollow, noarchive, nosnippet, noimageindex"
spec = importlib.util.spec_from_file_location("web_dist_test", ROOT / "tools/build_web_dist.py")
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)

with tempfile.TemporaryDirectory() as directory:
    base = Path(directory)
    assets = base / "assets"
    assets.mkdir()
    (assets / "index.html").write_text('<html><head><meta name="robots" content="index"></head><body>Study</body></html>')
    (assets / "sw.js").write_text("const BUILD_VERSION='dev';\nconst SHELL=['./index.html'];\n")
    (assets / "source_visuals").mkdir()
    (assets / "source_visuals/example.png").write_bytes(b"fixture-image")
    (assets / "Biochemistry_QBank_Source.pdf").write_bytes(b"fixture-pdf")
    with (assets / "Anatomy_QBank_Source.pdf").open("wb") as oversized:
        oversized.truncate(builder.PAGES_FILE_LIMIT + 1)
    for anatomy_url in ("https://source.example/anatomy.pdf", ""):
        (assets / "qbank-config.js").write_text("window.NK_QBANK_FIREBASE_CONFIG = " + json.dumps({"anatomyPdfUrl": anatomy_url}) + ";\n")
        out = base / ("with-worker" if anatomy_url else "without-worker")
        with patch.object(builder, "ASSETS", assets), patch.object(sys, "argv", ["build_web_dist.py", "--out", str(out), "--version", "fixture"]), contextlib.redirect_stdout(io.StringIO()):
            builder.main()
        page = (out / "index.html").read_text()
        assert page.count('name="robots"') == 1 and f'content="{DIRECTIVES}"' in page
        assert 'name="nk-qbank-build" content="fixture"' in page
        assert (out / "robots.txt").read_text() == "User-agent: *\nDisallow: /\n"
        headers = (out / "_headers").read_text()
        assert headers.startswith("/*\n  X-Robots-Tag: " + DIRECTIVES + "\n")
        assert "/sw.js\n  Cache-Control: no-cache" in headers
        assert "/source_visuals/*\n  Cache-Control: public, max-age=31536000, immutable" in headers
        assert "/vendor/*\n  Cache-Control: public, max-age=31536000, immutable" in headers
        assert (out / "source_visuals/example.png").read_bytes() == b"fixture-image"
        assert (out / "Biochemistry_QBank_Source.pdf").read_bytes() == b"fixture-pdf"
        assert (out / "_redirects").read_text() == "/* /index.html 200\n"
        if anatomy_url:
            assert json.loads((out / "_routes.json").read_text()) == {"version": 1, "include": ["/*"], "exclude": []}
            assert '"anatomyPdfUrl": "./anatomy-source.pdf"' in (out / "qbank-config.js").read_text()
            worker_source = (out / "_worker.js").read_text().replace("export default {", "const worker = {", 1)
            harness = r'''
const assert=(ok,message)=>{if(!ok)throw Error(message);};
const tag='noindex, nofollow, noarchive, nosnippet, noimageindex';
function excluded(response){assert(response.headers.get('X-Robots-Tag')===tag,'missing search exclusion');}
const requestHeaders={Range:'bytes=0-3','If-Range':'original','If-None-Match':'original','If-Modified-Since':'Wed, 01 Oct 2025 00:00:00 GMT'};
let upstreamRequest;
globalThis.fetch=async(url,options)=>{
  upstreamRequest={url,options};
  return new Response('%PDF',{status:206,headers:{'Content-Range':'bytes 0-3/100','Accept-Ranges':'bytes','ETag':'original','Cache-Control':'public, max-age=3600'}});
};
let response=await worker.fetch(new Request('https://app.example/anatomy-source.pdf',{headers:requestHeaders}),{});
excluded(response);assert(response.status===206,'range status');assert(await response.text()==='%PDF','stream bytes');
assert(response.headers.get('Content-Range')==='bytes 0-3/100','range header');
assert(response.headers.get('ETag')==='original','validator');assert(response.headers.get('Cache-Control')==='public, max-age=3600','upstream cache');
assert(response.headers.get('Content-Type')==='application/pdf','PDF type');
assert(upstreamRequest.url==='https://source.example/anatomy.pdf','source unchanged');
for(const [key,value] of Object.entries(requestHeaders))assert(upstreamRequest.options.headers.get(key)===value,'forwarded '+key);
for(const path of ['/index.html','/Biochemistry_QBank_Source.pdf','/source_visuals/example.png','/sw.js','/robots.txt','/unknown/dynamic/path']){
  let received;
  response=await worker.fetch(new Request('https://app.example'+path),{ASSETS:{fetch:async(request)=>{received=request;return new Response('unchanged',{status:200,headers:{'Cache-Control':'public, max-age=31536000, immutable','ETag':'asset'}});}}});
  excluded(response);assert(await response.text()==='unchanged','asset bytes');assert(new URL(received.url).pathname===path,'fallthrough route');
  assert(response.headers.get('Cache-Control')==='public, max-age=31536000, immutable','asset cache');assert(response.headers.get('ETag')==='asset','asset validator');
}
for(const status of [301,304,404]){
  response=await worker.fetch(new Request('https://app.example/fallback'),{ASSETS:{fetch:async()=>new Response(status===304?null:'fallback',{status,headers:{Location:'/index.html'}})}});
  excluded(response);assert(response.status===status,'fallback status');assert(response.headers.get('Location')==='/index.html','fallback location');
}
response=await worker.fetch(new Request('https://app.example/anatomy-source.pdf',{method:'POST'}),{});
excluded(response);assert(response.status===405&&response.headers.get('Allow')==='GET, HEAD','method rejection');
globalThis.fetch=async(url,options)=>{assert(options.method==='HEAD','head forwarding');return new Response(null,{status:200,headers:{'Content-Length':'100'}});};
response=await worker.fetch(new Request('https://app.example/anatomy-source.pdf',{method:'HEAD'}),{});
excluded(response);assert(response.status===200&&await response.text()===''&&response.headers.get('Content-Length')==='100','head response');
globalThis.fetch=async()=>new Response(null,{status:304,headers:{ETag:'original'}});
response=await worker.fetch(new Request('https://app.example/anatomy-source.pdf'),{});excluded(response);assert(response.status===304,'PDF not modified');
globalThis.fetch=async()=>{throw Error('offline');};
response=await worker.fetch(new Request('https://app.example/anatomy-source.pdf'),{});excluded(response);assert(response.status===502,'source error');
console.log('CRAWLER_WORKER_OK static/dynamic/pdf/errors/ranges/validators/head/cache/body');
'''
            script = base / "worker-test.mjs"
            script.write_text(worker_source + harness)
            subprocess.run(["node", str(script)], check=True)
        else:
            assert not (out / "_worker.js").exists()
            assert not (out / "_routes.json").exists()

print("CRAWLER_EXCLUSION_OK robots/meta/global_headers/worker_fallthrough/cache_unchanged/content_unchanged")
