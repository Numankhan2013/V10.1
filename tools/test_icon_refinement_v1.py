#!/usr/bin/env python3
"""Actual shared factories retain sizes, names, offline geometry and fallbacks."""
from pathlib import Path
import subprocess
import tempfile
from app_page import app_source

ROOT = Path(__file__).resolve().parents[1]


def main():
    app=app_source();core=(ROOT/'app/src/main/modules/icon_refinement.js').read_text()
    assert app.count(core)==1 and app.count('NK_ICON_REFINEMENT_V1_START')==1
    assert app.index('NK_INTERACTION_POLISH_V1_END')<app.index(core)<app.index('  window.QB={')
    for anchor in ['NK_INTERACTION_POLISH_V1_END','  window.QB={','function nkSubjectGraphic(','function nkAnalysisIcon(','function navIcon(']:
        assert app.count(anchor)==1,f'Icon owner anchor mismatch: {anchor}'
    nav=app[app.index('  function navIcon('):app.index('\n  function logo')]
    subject=app[app.index('function nkAppSubjectMeta('):app.index('  function nkFlameGraphic')]
    analysis=(ROOT/'app/src/main/modules/refined_analysis.js').read_text().split('  function nkAnalysisTest')[0]
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
const collectionKeys={'Biochemistry':'biochemistry','Poisoning & Environmental Exposure':'poisoning','Ophthalmology':'ophthalmology','Biostatistics & Epidemiology':'biostatistics','Male Reproductive System':'male-reproductive','Female Reproductive System & Breast':'female-reproductive','Pregnancy, Childbirth & Puerperium':'pregnancy','Future Collection':'uworld'};
const glyphs=new Set();
for(const [name,key] of Object.entries(collectionKeys)){
  const icon=nkSubjectGraphic('UWorld · '+name,24);
  assert(icon.includes(`data-nk-icon="${key}"`),name);
  assert(!icon.includes('undefined')&&!icon.includes('http'));
  glyphs.add(icon);
}
assert.equal(glyphs.size,Object.keys(collectionKeys).length,'collections must not silently share the DNA fallback');
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
