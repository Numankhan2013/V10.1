#!/usr/bin/env python3
"""Contract and behavior for My Subjects professional-year groups on Home.

Anatomy, Physiology and Biochemistry sit under First Prof; Microbiology sits
under Second Prof. Groups open collapsed, remember their state per device, and
a subject that has no group yet still gets a card under Other, so a new bank
can never disappear from Home.
"""
from pathlib import Path
import json
import re
import subprocess

from app_page import app_source, css_section

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "app/src/main/assets/index.html"
MARKER = "NK_PROF_GROUPS_V1"
STYLE_ID = "nk-professional-groups-v1"


def main():
    html = app_source()
    script = next(x for x in re.findall(r"<script>(.*?)</script>", html, re.S) if f"{MARKER}_START" in x)
    subprocess.run(["node", "--check"], input=script, text=True, check=True)

    required = (
        MARKER,
        "NK_PROF_GROUP_BY_SUBJECT",
        "Anatomy:'first'", "Physiology:'first'", "Biochemistry:'first'", "Microbiology:'second'",
        "First Prof", "Second Prof", "Other",
        "nkProfGroupSubjects", "nkProfGroupMarkup", "nkProfGroupsMarkup", "nkToggleProfGroup",
        "nk-prof-groups", "nk-prof-group", "nk-prof-head", "nk-prof-copy", "nk-prof-count", "nk-prof-chevron", "nk-prof-body",
        "aria-expanded", "aria-controls", "inert",
        "qbank_prof_groups_v1",
        "nkSubjectCardV3",
    )
    missing = [x for x in required if x not in html]
    if missing:
        raise SystemExit(f"Professional group contract missing: {missing}")

    if html.count(f"function nkToggleProfGroup(") != 1:
        raise SystemExit("nkToggleProfGroup duplicated or missing")
    if "nkToggleProfGroup," not in html.split("window.QB={", 1)[1]:
        raise SystemExit("window.QB does not expose nkToggleProfGroup")
    home = html.split("function dashboard(){", 1)[1].split("function testRow(", 1)[0]
    if '<div class="nk-prof-groups">${nkProfGroupsMarkup()}</div>' not in home:
        raise SystemExit("Home does not render the professional groups in My Subjects")
    if 'nk-home-subjects"><div class="nk-v3-section-head"' not in home:
        raise SystemExit("My Subjects section head changed shape")

    css = css_section(STYLE_ID)
    for rule in ("grid-template-rows:0fr", ".nk-prof-group.is-open .nk-prof-body", "prefers-reduced-motion", "overflow:hidden"):
        if rule not in css:
            raise SystemExit(f"Professional group stylesheet missing: {rule}")
    if "display:none" in css:
        raise SystemExit("Professional groups must stay in the accessibility tree, not display:none")

    # Behavior: render, Other fallback, toggle, persistence and the QB export.
    section = (
        "function nkSubjectCardV3("
        + html.split("function nkSubjectCardV3(", 1)[1].split(f"/* {MARKER}_END */", 1)[0]
    )

    behavior = r'''
const assert=require('node:assert/strict'),vm=require('node:vm');
function el(){
  const self={
    attrs:new Set(),kv:{},cls:new Set(),
    setAttribute(k,v){self.kv[k]=String(v);},
    getAttribute(k){return k in self.kv?self.kv[k]:null;},
    toggleAttribute(k,on){if(on)self.attrs.add(k);else self.attrs.delete(k);},
    removeAttribute(k){self.attrs.delete(k);},
    hasAttribute(k){return self.attrs.has(k);}
  };
  self.classList={contains:c=>self.cls.has(c),toggle:(c,on)=>{if(on)self.cls.add(c);else self.cls.delete(c);}};
  return self;
}
const heads={},bodies={},groups={};
['first','second'].forEach(id=>{
  const head=el(),body=el(),group=el();
  body.toggleAttribute('inert',true);
  group.querySelector=sel=>sel==='.nk-prof-head'?head:sel==='.nk-prof-body'?body:null;
  groups[id]=group;heads[id]=head;bodies[id]=body;
});
const store={data:{},getItem:function(k){return k in this.data?this.data[k]:null;},setItem:function(k,v){this.data[k]=String(v);}};
const context={
  SUBJECTS:[
    {subject:'Biochemistry',topics:[],questions:[]},
    {subject:'Physiology',topics:[],questions:[]},
    {subject:'Anatomy',topics:[],questions:[]},
    {subject:'Microbiology',topics:[],questions:[]}
  ],
  localStorage:store,
  document:{querySelector:sel=>{const m=/data-nk-prof="(\w+)"/.exec(sel);return m&&groups[m[1]]?groups[m[1]]:null;}},
  esc:String,fmtNum:value=>String(value),navIcon:()=>'',
  nkAppSubjectMeta:()=>({key:'subject'}),nkAppSubjectIcon:()=>'',
  nkBankRecords:()=>[],qAttempts:()=>[],
  nkSubjectStatsV3:()=>({topics:1,questions:2,pct:0})
};
context.window={QB:{}};
vm.createContext(context);
vm.runInContext(SOURCE,context);
let markup=vm.runInContext('nkProfGroupsMarkup()',context);
assert.ok(markup.includes('data-nk-prof="first"')&&markup.includes('data-nk-prof="second"'));
assert.ok(!markup.includes('data-nk-prof="other"'),'Other must stay hidden while every subject has a group');
assert.ok(markup.indexOf('Biochemistry')<markup.indexOf('data-nk-prof="second"'),'First Prof keeps the three first-year subjects');
assert.ok(markup.indexOf('Microbiology')>markup.indexOf('data-nk-prof="second"'),'Microbiology belongs to Second Prof');
assert.ok(markup.includes('aria-expanded="false"')&&!markup.includes('is-open'),'groups open collapsed');
assert.equal((markup.match(/ inert aria-hidden="true"/g)||[]).length,2,'collapsed groups are inert');
assert.ok(markup.includes('3 subjects')&&markup.includes('1 subject'),'group counts use singular and plural');
assert.ok(markup.includes('data-nk-banks="[]"'),'subject cards keep the bank progress contract');
assert.equal((markup.match(/<button class="nk-v3-subject-card/g)||[]).length,4,'every subject keeps one card');
// A subject with no group yet stays reachable under Other.
context.SUBJECTS=context.SUBJECTS.concat([{subject:'Pathology',topics:[],questions:[]}]);
markup=vm.runInContext('nkProfGroupsMarkup()',context);
assert.ok(markup.includes('data-nk-prof="other"')&&markup.includes('Pathology'),'unknown subjects fall back to Other');
assert.deepEqual(vm.runInContext("nkProfGroupSubjects('other')",context),['Pathology']);
assert.deepEqual(vm.runInContext("nkProfGroupSubjects('second')",context),['Microbiology']);
// Toggle updates the DOM contract and remembers the choice per device.
vm.runInContext("nkToggleProfGroup('second')",context);
assert.ok(groups.second.cls.has('is-open')&&heads.second.kv['aria-expanded']==='true');
assert.ok(!bodies.second.hasAttribute('inert')&&!('aria-hidden' in bodies.second.kv));
assert.equal(store.data['qbank_prof_groups_v1'],'{"second":true}');
assert.ok(vm.runInContext('nkProfGroupsMarkup()',context).includes('is-second is-open'));
vm.runInContext("nkToggleProfGroup('second')",context);
assert.ok(!groups.second.cls.has('is-open')&&heads.second.kv['aria-expanded']==='false'&&bodies.second.hasAttribute('inert'));
assert.equal(store.data['qbank_prof_groups_v1'],'{"second":false}');
// Reopening one group never opens the other.
vm.runInContext("nkToggleProfGroup('first')",context);
const after=vm.runInContext('nkProfGroupsMarkup()',context);
assert.ok(after.includes('is-first is-open')&&after.includes('id="nk-prof-body-first"')&&!after.includes('is-second is-open'));
assert.ok(after.includes('id="nk-prof-body-second" inert'),'Second Prof stays closed while First Prof is open');
assert.ok(!vm.runInContext("nkToggleProfGroup('missing')",context),'unknown group ids are ignored');
console.log('PROF_GROUPS_BEHAVIOR_OK groups=2 other=fallback collapse=default persist=local');
'''
    behavior = behavior.replace("SOURCE", json.dumps(section))
    done = subprocess.run(["node", "-e", behavior], capture_output=True, text=True, cwd=str(ROOT))
    if done.returncode:
        raise SystemExit(f"Professional group behavior failed:\n{done.stdout}{done.stderr}")
    print(done.stdout.strip())

    if HTML.read_text(encoding="utf-8").count(f"{MARKER}_START") != 1:
        raise SystemExit("Professional group block duplicated in index.html")
    print("PROFESSIONAL_SUBJECT_GROUPS_OK first=3 second=1 collapsed=default")


if __name__ == "__main__":
    main()
