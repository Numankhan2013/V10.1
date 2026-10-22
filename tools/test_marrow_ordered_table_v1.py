#!/usr/bin/env python3
"""The ordered-block explanation renderer must not print object tokens.

`nkRenderMarrowOrderedTable` renders a structured table cell by cell. The
base renderer routes every table through `nkNormalizeMarrowStructuredTable`
first, which flattens object-shaped columns and cells to text. The ordered
path skipped that normaliser, so a table whose columns or rows are objects
rendered "[object Object]" to the learner.

The two functions are taken out of the assembled page and driven directly,
with the table shapes the shipped banks actually use:

- object columns plus object rows keyed by the column key (Anatomy Marrow),
- object columns plus array rows of {label, value} cells,
- the plain string form, which must keep working.
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

RUNTIME = r"""
const assert=require('assert'),fs=require('fs');
const page=fs.readFileSync(process.argv[2],'utf8');
// Take the shipped functions out of the assembled page.
const grab=name=>{
  const needle='  function '+name+'(';
  const start=page.indexOf(needle);
  if(start<0)throw new Error('missing '+name);
  let depth=0,i=start+needle.length-1;
  for(;i<page.length;i++){
    const c=page[i];
    if(c==='{')depth++;
    else if(c==='}'){depth--;if(depth===0)break;}
  }
  return page.slice(start,i+1);
};
const esc=x=>String(x??'');
const nkMarrowRich=x=>String(x??'');
eval(grab('nkMarrowTableCellText'));
eval(grab('nkNormalizeMarrowStructuredTable'));
eval(grab('nkMarrowOrderedCell'));
eval(grab('nkRenderMarrowOrderedTable'));

// 1. Object columns with object rows keyed by the column key.
//    This is the shape the Anatomy Marrow bank ships.
const keyedTable={
  table_id:'t1',
  title:'Pharyngeal arch muscle derivatives',
  columns:[{key:'arch',label:'Pharyngeal Arch'},{key:'muscle_derivatives',label:'Muscle derivatives'}],
  rows:[{arch:'I',muscle_derivatives:'Muscles of mastication, mylohyoid'}],
};
const keyed=nkRenderMarrowOrderedTable(keyedTable);
assert(!keyed.includes('[object Object]'),'the ordered renderer printed an object token: '+keyed);
assert(keyed.includes('Pharyngeal Arch')&&keyed.includes('Muscle derivatives'),'the ordered renderer lost the column labels: '+keyed);
assert(keyed.includes('Muscles of mastication, mylohyoid'),'the ordered renderer lost the row text: '+keyed);
assert(keyed.includes('>I</td>'),'the ordered renderer lost the keyed cell: '+keyed);

// 2. Object columns with array rows of {label, value} cells.
//    The normaliser flattens each cell through nkMarrowTableCellText, which
//    prefers the label, so the ordered path must show the same text.
const cellTable={
  table_id:'t2',
  columns:[{key:'statement',label:'Statement'},{key:'choice',label:'Choice'}],
  rows:[[{label:'1',value:'Inhibitory'},{label:'2',value:'Excitatory'}]],
};
const cells=nkRenderMarrowOrderedTable(cellTable);
assert(!cells.includes('[object Object]'),'the ordered renderer printed an object token: '+cells);
assert(cells.includes('Statement')&&cells.includes('Choice'),'the ordered renderer lost the column labels: '+cells);
assert(cells.includes('>1</td>')&&cells.includes('>2</td>'),'the ordered renderer lost the cell text: '+cells);

// 3. The plain string form must keep working.
const plainTable={table_id:'t3',columns:['A','B'],rows:[['one','two']]};
const plain=nkRenderMarrowOrderedTable(plainTable);
assert(plain.includes('one')&&plain.includes('two'),'the ordered renderer lost a plain table: '+plain);
assert(!plain.includes('[object Object]'),'the ordered renderer printed an object token: '+plain);

console.log('MARROW_ORDERED_TABLE_OK keyed_rows=flattened object_cells=flattened plain_cells=kept');
"""


def main() -> None:
    import sys

    sys.path.insert(0, str(ROOT / "tools"))
    from app_page import app_page

    with tempfile.NamedTemporaryFile("w", suffix=".js", encoding="utf-8", delete=False) as handle:
        handle.write(RUNTIME)
        script = Path(handle.name)
    page = ROOT / "build" / "ordered-table-page.js"
    page.parent.mkdir(parents=True, exist_ok=True)
    page.write_text(app_page(), encoding="utf-8")
    try:
        subprocess.run(["node", str(script), str(page)], check=True, cwd=ROOT)
    finally:
        script.unlink(missing_ok=True)
        page.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
