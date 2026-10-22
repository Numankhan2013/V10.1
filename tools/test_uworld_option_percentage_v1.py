#!/usr/bin/env python3
"""A reviewed UWorld question without statistics must still render.

`nkUworldOptionPercentage` reads the reviewed document's
`statistics.selection_percent`. A reviewed document without statistics made
the function throw while building the option list, which aborted the whole
question render.

The function is taken out of the shipped module and driven directly with the
document shapes the banks can carry.
"""

from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "app/src/main/modules/uworld_biochemistry.js"

HARNESS = r"""
const assert=require('assert'),fs=require('fs');
const SOURCE=fs.readFileSync(process.argv[2],'utf8');
function grab(name){
  const needle='  function '+name+'(';
  const start=SOURCE.indexOf(needle);
  if(start<0)throw new Error('missing '+name);
  let depth=0,i=start+needle.length-1;
  for(;i<SOURCE.length;i++){
    const c=SOURCE[i];
    if(c==='{')depth++;
    else if(c==='}'){depth--;if(depth===0)break;}
  }
  return SOURCE.slice(start,i+1);
}
const esc=x=>String(x??'');
eval(grab('nkUworldOptionPercentage'));

// A reviewed document with no statistics at all.
const withoutStatistics={id:'u1',uworldDocument:{question:'q',options:[{letter:'A',text:'a'}],question_blocks:[],explanation:[]}};
assert.equal(nkUworldOptionPercentage(withoutStatistics,{letter:'A'}),'',
  'a reviewed document without statistics must render no percentage');

// A reviewed document whose statistics carry no selection percentages.
const withoutPercentages={id:'u2',uworldDocument:{question:'q',options:[{letter:'A',text:'a'}],question_blocks:[],explanation:[],statistics:{answered_correctly_percent:41}}};
assert.equal(nkUworldOptionPercentage(withoutPercentages,{letter:'A'}),'',
  'a reviewed document without selection percentages must render no percentage');

// A reviewed document with selection percentages still shows them.
const withPercentages={id:'u3',uworldDocument:{question:'q',options:[{letter:'A',text:'a'}],question_blocks:[],explanation:[],statistics:{selection_percent:{A:37}}}};
assert(nkUworldOptionPercentage(withPercentages,{letter:'A'}).includes('37%'),
  'the source percentage must still be shown: '+nkUworldOptionPercentage(withPercentages,{letter:'A'}));

console.log('UWORLD_OPTION_PERCENTAGE_OK missing_statistics=guarded percentages=shown');
"""


def main() -> None:
    with tempfile.NamedTemporaryFile("w", suffix=".js", encoding="utf-8", delete=False) as handle:
        handle.write(HARNESS)
        script = Path(handle.name)
    try:
        subprocess.run(["node", str(script), str(MODULE)], check=True, cwd=ROOT)
    finally:
        script.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
