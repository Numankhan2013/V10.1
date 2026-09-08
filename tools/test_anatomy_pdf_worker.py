"""Verify same-origin source streaming without fetching or altering medical content."""
from pathlib import Path
import subprocess,tempfile,json
p=Path(__file__).with_name('anatomy_pdf_worker.mjs')
s=p.read_text().replace('__ANATOMY_SOURCE_URL__',json.dumps('https://source.example/anatomy.pdf'))
s+='''
const worker=(await import(import.meta.url)).default;
const assert=(v)=>{if(!v)throw Error('Worker contract failed');};
let seen;
globalThis.fetch=async(url,options)=>{seen={url,options};return new Response('%PDF',{status:206,headers:{'Content-Range':'bytes 0-3/100','ETag':'original'}});};
const response=await worker.fetch(new Request('https://app.example/anatomy-source.pdf',{headers:{Range:'bytes=0-3'}}),{});
assert(response.status===206);assert(await response.text()==='%PDF');assert(response.headers.get('Content-Range')==='bytes 0-3/100');assert(seen.options.headers.get('Range')==='bytes=0-3');assert(seen.url==='https://source.example/anatomy.pdf');
assert((await worker.fetch(new Request('https://app.example/anatomy-source.pdf',{method:'POST'}),{})).status===405);
const asset=await worker.fetch(new Request('https://app.example/index.html'),{ASSETS:{fetch:()=>new Response('asset')}});assert(await asset.text()==='asset');
console.log('ANATOMY_STREAM_WORKER_OK range/body/asset fallback/methods');
'''
# Reference the default object directly; no self-import during module evaluation.
s=s.replace('export default {','const worker = {',1).replace('const worker=(await import(import.meta.url)).default;','')
with tempfile.NamedTemporaryFile(suffix='.mjs',mode='w') as f:
 f.write(s);f.flush();subprocess.run(['node',f.name],check=True)
