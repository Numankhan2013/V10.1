#!/usr/bin/env python3
"""Every browse filter must match a query word by word, not as one phrase.

Four filters — the Revision browse list, the Notes list, the Coverage topic
list and the module-builder topic picker — tested the whole typed phrase with
`includes`, so a query only matched when its words happened to be adjacent in
the row. The question search already tokenises, so the same query worked
there and nowhere else.

The filters are taken out of the shipped modules and driven directly, against
both the rendered page and the live filter that runs as the learner types.
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from js_extract import extract_function  # noqa: E402

REVISION = ROOT / "app/src/main/modules/revision_desk.js"
NOTES = ROOT / "app/src/main/modules/question_notes.js"
COVERAGE = ROOT / "app/src/main/modules/qbank_coverage.js"
MODULES = ROOT / "app/src/main/modules/study_modules.js"

RUNTIME = r"""
const assert=require('assert');

// ---------------------------------------------------------------- fake DOM --
function item(search){return {dataset:{revisionSearch:search,noteSearch:search},hidden:false};}
const revisionItems=[item('biochemistry · marrow · topic which enzyme is deficient here'),
                     item('anatomy · prepladder · topic heart valve anatomy')];
const noteItems=[item('cardiology murmur notes'),item('renal physiology notes')];
const moduleButtons=[{text:'Cardiac muscle physiology',hidden:false},{text:'Skeletal muscle anatomy',hidden:false}];
// Each topic button carries its title in a <strong>, like the shipped markup.
for(const button of moduleButtons){
  button.querySelector=()=>({textContent:button.text});
}
const moduleGroups=[{title:'Anatomy',buttons:moduleButtons}];
for(const group of moduleGroups){
  group.querySelector=selector=>selector==='.nk-module-group-title'?{textContent:group.title}:null;
  group.querySelectorAll=()=>group.buttons;
}
const emptyNotice={hidden:false};
global.document={
  querySelectorAll:selector=>selector==='.nk-revision-item'?revisionItems
    :selector==='.nk-notes-item'?noteItems
    :selector==='.nk-module-topic-group[data-subject-index]'?moduleGroups:[],
  querySelector:selector=>selector.endsWith('no-match')?emptyNotice:null,
  getElementById:()=>null,
};
global.route={page:'revision-browse',id:'bookmarks'};
global.nkRevisionBrowseQueries={wrong:'',bookmarks:''};
global.nkRevisionBrowseAccount='';
global.nkNotesQuery='';
global.nkCoverageBankKey='';
global.nkCoverageStatus='all';
global.nkCoverageSearch='';
global.nkCoverageExpanded=true;
global.activeSubject='Anatomy';
global.esc=x=>String(x??'');
global.navIcon=()=>'';
global.fmtNum=String;
global.shell=x=>x;
global.nkAppEmpty=()=>'<p>empty</p>';
global.nkRevisionScopeLabel=()=>'All subjects';
global.nkAuth={uid:'account-one'};
global.nkRevisionDeskData=()=>({wrong:[],bookmarked:[
  {id:'bio-1',subject:'Biochemistry',bank:'Marrow',chapter:'Topic',question:'Which enzyme is deficient here'},
  {id:'anat-1',subject:'Anatomy',bank:'PrepLadder',chapter:'Topic',question:'Heart valve anatomy'}],
});
global.nkCoverageData=()=>({banks:[{key:'anat-marrow',subject:'Anatomy',bank:'Marrow',topics:[
  {title:'Cardiac muscle physiology',attempted:1,total:2,topicId:'t1',subject:'Anatomy',bank:'Marrow'},
  {title:'Skeletal muscle anatomy',attempted:0,total:2,topicId:'t2',subject:'Anatomy',bank:'Marrow'}]}]});

__FUNCTIONS__

// ------------------------------------------------------- revision browse ----
global.nkRevisionBrowseQueries={wrong:'',bookmarks:''};
nkRevisionBrowseQueries.bookmarks='enzyme deficient';
const page=nkRevisionBrowsePage('bookmarks');
const rows=page.split('<article class="nk-revision-item"');
const matched=rows.find(part=>part.includes('deficient'));
assert(matched,'the rendered page must contain the matching row');
assert(!matched.startsWith(' hidden'),
  'the rendered page must not hide a row whose query words are not adjacent: '+matched.slice(0,120));

// The live filter must do the same as the learner types.
nkFilterRevisionBrowse('enzyme deficient');
assert.equal(revisionItems[0].hidden,false,'the live filter must keep a row whose query words are not adjacent');
assert.equal(revisionItems[1].hidden,true,'the live filter must hide a row that does not match');
nkFilterRevisionBrowse('heart valve');
assert.equal(revisionItems[1].hidden,false,'the live filter must match a multi-word query');
assert.equal(revisionItems[0].hidden,true,'the live filter must hide a row that does not match');
nkFilterRevisionBrowse('');
assert.equal(revisionItems[0].hidden,false,'an empty query must show every row');
assert.equal(revisionItems[1].hidden,false,'an empty query must show every row');

// --------------------------------------------------------------- notes ------
nkFilterNotes('cardiology murmur');
assert.equal(noteItems[0].hidden,false,'the notes filter must match a multi-word query');
assert.equal(noteItems[1].hidden,true,'the notes filter must hide a row that does not match');
nkFilterNotes('renal notes');
assert.equal(noteItems[1].hidden,false,'the notes filter must match words that are not adjacent');
assert.equal(noteItems[0].hidden,true,'the notes filter must hide a row that does not match');

// ------------------------------------------------------------ coverage ------
nkCoverageSearch='cardiac physiology';
const coverage=nkCoverageListMarkup(nkCoverageData());
assert(coverage.includes('Cardiac muscle physiology'),'the coverage search must match words that are not adjacent');
assert(!coverage.includes('Skeletal muscle anatomy'),'the coverage search must hide a topic that does not match');
nkCoverageSearch='cardiac';
assert(nkCoverageListMarkup(nkCoverageData()).includes('Cardiac muscle physiology'),'a single-word coverage search must still work');
assert(!nkCoverageListMarkup(nkCoverageData()).includes('Skeletal muscle anatomy'),'a single-word coverage search must not match the other topic');

// ------------------------------------------------------ module builder ------
global.document.querySelectorAll=selector=>selector==='.nk-module-topic-group[data-subject-index]'?moduleGroups:[];
nkFilterModuleTopics('cardiac physiology');
assert.equal(moduleButtons[0].hidden,false,'the module topic picker must match a multi-word query');
assert.equal(moduleButtons[1].hidden,true,'the module topic picker must hide a topic that does not match');
nkFilterModuleTopics('skeletal');
assert.equal(moduleButtons[1].hidden,false,'a single-word module topic search must still work');
assert.equal(moduleButtons[0].hidden,true,'a single-word module topic search must not match the other topic');

console.log('SEARCH_FILTERS_OK revision=tokenised notes=tokenised coverage=tokenised modules=tokenised');
"""


def main() -> None:
    pieces = [
        extract_function(REVISION.read_text(encoding="utf-8"), "nkRevisionBrowsePage"),
        extract_function(REVISION.read_text(encoding="utf-8"), "nkFilterRevisionBrowse"),
        extract_function(NOTES.read_text(encoding="utf-8"), "nkFilterNotes"),
        extract_function(COVERAGE.read_text(encoding="utf-8"), "nkCoverageSelected"),
        extract_function(COVERAGE.read_text(encoding="utf-8"), "nkCoverageListMarkup"),
        extract_function(MODULES.read_text(encoding="utf-8"), "nkFilterModuleTopics"),
    ]
    script_text = RUNTIME.replace("__FUNCTIONS__", "\n".join(pieces))
    with tempfile.NamedTemporaryFile("w", suffix=".js", encoding="utf-8", delete=False) as handle:
        handle.write(script_text)
        script = Path(handle.name)
    try:
        subprocess.run(["node", str(script)], check=True, cwd=ROOT)
    finally:
        script.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
