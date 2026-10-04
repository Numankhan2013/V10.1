#!/usr/bin/env python3
"""Actual shared factories retain sizes, names, offline geometry and fallbacks."""
from pathlib import Path
import subprocess
import tempfile
from apply_icon_refinement_v1 import transform, MARKER
from apply_whole_app_vision_v1 import FOUNDATION_AND_DASHBOARD

ROOT = Path(__file__).resolve().parents[1]


def main():
    source = '<html><body><script>/* NK_INTERACTION_POLISH_V1_END */\nfunction nkSubjectGraphic(){}\nfunction nkAnalysisIcon(){}\n  window.QB={};</script><button onclick="QB.goIndex(1)">Next</button></body></html>'
    result=transform(source);core=(ROOT/'tools/icon_refinement_core.js').read_text()
    assert result.replace(core+'\n','',1)==source
    assert transform(result)==result
    try:
        transform(source.replace('function nkSubjectGraphic(','unexpectedOwner('))
    except ValueError:
        pass
    else:
        raise AssertionError('missing canonical factory accepted')
    app=(ROOT/'app/src/main/assets/index.html').read_text()
    nav=app[app.index('  function navIcon('):app.index('\n  function logo')]
    subject=FOUNDATION_AND_DASHBOARD.split('  function nkFlameGraphic')[0]
    analysis=(ROOT/'tools/refined_analysis_core.js').read_text().split('  function nkAnalysisTest')[0]
    checks=r'''
const assert=require('node:assert/strict');
const names=['menu','bell','search','home','book','test','chart','bookmark','back','chevron','share','star','check','close','more','clock','trash','refresh','grid','heart','body','molecule','dna','bulb','pause'];
for(const name of names){for(const size of [14,18,22,28]){
  const icon=navIcon(name,size);
  assert(icon.includes(`width="${size}" height="${size}"`),name);
  assert(icon.includes('aria-hidden="true"')&&icon.includes('focusable="false"'));
  assert(icon.includes(`data-nk-icon="${name}"`));
  assert.equal((icon.match(/<svg\b/g)||[]).length,1);
  assert(!/on\w+=|<filter|<image|<animate|<script|https?:/.test(icon));
}}
for(const name of ['Anatomy','Physiology','Biochemistry']){
  const icon=nkSubjectGraphic(name,22);assert(icon.includes('nk-subject-svg'));assert(icon.includes('nk-icon-tone'));
}
const collectionKeys={'Biochemistry':'biochemistry','Poisoning & Environmental Exposure':'poisoning','Ophthalmology':'ophthalmology','Male Reproductive System':'male-reproductive','Female Reproductive System & Breast':'female-reproductive','Pregnancy, Childbirth & Puerperium':'pregnancy','Future Collection':'uworld'};
const glyphs=new Set();
for(const [name,key] of Object.entries(collectionKeys)){
  const icon=nkSubjectGraphic('UWorld · '+name,24);
  assert(icon.includes(`data-nk-icon="${key}"`),name);
  assert(!icon.includes('undefined')&&!icon.includes('http'));
  glyphs.add(icon);
}
assert.equal(glyphs.size,7,'collections must not silently share the DNA fallback');
for(const name of ['minus','edit','timer'])assert(nkAnalysisIcon(name,18).includes('nk-product-icon'));
assert(navIcon('future').includes('circle'),'unknown glyph fallback retained');
console.log('ICON_REFINEMENT_OK glyphs=25 sizes=14,18,22,28 subject_families=3 offline=true');
'''
    with tempfile.TemporaryDirectory() as td:
        path=Path(td)/'icons.js';path.write_text(nav+subject+analysis+core+checks)
        subprocess.run(['node',str(path)],check=True)
    print('ICON_REFINEMENT_OWNER_OK existing_bytes_preserved=true')


if __name__ == '__main__':
    main()
