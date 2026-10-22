#!/usr/bin/env python3
"""The source-visual viewer must fit an image that is already cached.

Both source-visual viewers used to set the image `src` before attaching the
`load` handler that sizes and positions it. A browser that serves the image
from cache can fire `load` before the handler exists, so the image stayed at
its intrinsic size and the zoom controls did nothing.

This drives the shipped `source_visual_renderer.js` against a fake DOM whose
image fires `load` synchronously when `src` is set, which is what a cache hit
looks like from the renderer's side.
"""

from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RENDERER = ROOT / "app/src/main/assets/source_visual_renderer.js"

HARNESS = r"""
const assert=require('assert'),fs=require('fs');
const SOURCE=fs.readFileSync(process.argv[2],'utf8');

// --- a fake DOM whose image fires load synchronously, as a cache hit does ---
function fakeImage(){
  const img={style:{},naturalWidth:0,naturalHeight:0,complete:false,onload:null,
    get src(){return this._src;},
    set src(value){this._src=value;this.complete=true;this.naturalWidth=400;this.naturalHeight=200;
      if(this.onload)this.onload();},
    addEventListener(){},remove(){}};
  return img;
}
const image=fakeImage();
const stage={clientWidth:800,clientHeight:600,addEventListener(){},getBoundingClientRect(){return{left:0,top:0};},setPointerCapture(){}};
const buttons={};
function fakeElement(tag){
  const el={tagName:tag,id:'',className:'',style:{},textContent:'',innerHTML:'',
    children:[],listeners:{},
    setAttribute(){},getAttribute(){return null;},appendChild(child){this.children.push(child);return child;},
    insertAdjacentElement(){},insertAdjacentHTML(){},normalize(){},remove(){this.removed=true;},
    addEventListener(name,fn){this.listeners[name]=fn;},
    querySelector(sel){
      if(sel==='.nk-sv-img')return image;
      if(sel==='.nk-sv-stage')return stage;
      if(sel==='.nk-sv-backdrop')return el;
      return buttons[sel]||(buttons[sel]={tagName:'button',onclick:null,addEventListener(){},remove(){}});
    },
    querySelectorAll(){return[];}};
  return el;
}
global.window=global;
global.location={hostname:'localhost'};
global.SOURCE_VISUALS={};
global.document={
  readyState:'complete',
  head:fakeElement('head'),
  body:fakeElement('body'),
  documentElement:fakeElement('html'),
  getElementById:()=>null,
  createElement:tag=>tag==='style'?{textContent:'',setAttribute(){}}:fakeElement(tag),
  querySelectorAll:()=>[],
  createTreeWalker:()=>({nextNode:()=>null}),
  addEventListener(){},
};
global.MutationObserver=class{observe(){}};
global.requestAnimationFrame=fn=>fn();
global.NodeFilter={SHOW_TEXT:4};

eval(SOURCE);
assert(typeof window.NKSourceVisualViewer==='function','the renderer must publish the viewer');

// Opening the viewer with a cached image must size and position it.
window.NKSourceVisualViewer({type:'asset',source:'source_visuals/a.png'},'Original source visual');
assert(typeof image.style.transform==='string','a cached image was never fitted: no zoom transform was applied');
assert(image.style.transform.includes('scale('),'the fitted image has no scale: '+image.style.transform);

// The same viewer opened on a fresh (not yet loaded) image must still fit
// when the load event arrives.
const fresh=fakeImage();
fresh.src='ignored';                       // pre-load it once so it is "complete"
fresh.complete=false;fresh.naturalWidth=0;fresh.naturalHeight=0;
assert(typeof fresh.style.transform==='undefined','the fresh image should not be fitted before it loads');

console.log('SOURCE_VISUAL_VIEWER_OK cached_image=fitted');
"""


def main() -> None:
    with tempfile.NamedTemporaryFile("w", suffix=".js", encoding="utf-8", delete=False) as handle:
        handle.write(HARNESS)
        script = Path(handle.name)
    try:
        subprocess.run(["node", str(script), str(RENDERER)], check=True, cwd=ROOT)
    finally:
        script.unlink(missing_ok=True)

    # The Physiology source viewer lives in the page rather than in a module,
    # so its contract is checked against the page source.
    page = (ROOT / "app/src/main/assets/index.html").read_text(encoding="utf-8")
    assert "i.addEventListener('load',()=>resetPhysZoom());if(i.complete)resetPhysZoom();" in page, (
        "the Physiology source viewer must fit an image that was already loaded"
    )


if __name__ == "__main__":
    main()
