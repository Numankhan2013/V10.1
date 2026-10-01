#!/usr/bin/env python3
"""Exercise actual table normalizer against both immutable source schemas."""
import ast
import json
import subprocess
from pathlib import Path

from inventory_marrow_explanations import load_sharded

ROOT = Path(__file__).resolve().parents[1]


def main():
    tree = ast.parse((ROOT / 'tools/apply_marrow_structured_table_renderer_v1.py').read_text())
    helper = next(ast.literal_eval(node.value) for node in tree.body
                  if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'helper' for t in node.targets))
    anatomy, _ = load_sharded('anatomy_ch001_063')
    physio, _ = load_sharded('physiology_ch001_043')
    sources = {q['id']: q for q in anatomy['questions'] + physio['questions']}
    keyed = sources['marrow__ANAT_CH05_Q010']['structuredExplanation']['tables'][0]
    alias = sources['marrow__PHYSIO_CH42_Q008']['structuredExplanation']['tables'][0]
    script = helper + '''
    const fs=require('fs'),assert=require('assert');
    const [keyed,alias]=JSON.parse(fs.readFileSync(0,'utf8'));
    const before=JSON.stringify([keyed,alias]);
    const first=nkNormalizeMarrowStructuredTable(keyed);
    assert.deepStrictEqual(first.columns,['Pharyngeal Arch','Muscle derivatives']);
    assert.strictEqual(first.rows.length,5);
    assert(first.rows.some(row=>row.some(cell=>cell.includes('Larynx - cricothyroid'))));
    const second=nkNormalizeMarrowStructuredTable(alias);
    assert.deepStrictEqual(second.columns,alias.headers);
    assert.deepStrictEqual(second.rows,alias.rows);
    assert.strictEqual(second.rows.length,3);
    assert.strictEqual(second.rows[1][4],'Increased LH surge');
    assert.deepStrictEqual(nkNormalizeMarrowStructuredTable({...alias,columns:[]}),second);
    assert.deepStrictEqual(nkNormalizeMarrowStructuredTable({columns:null,rows:null}),{columns:null,rows:null});
    assert.strictEqual(JSON.stringify([keyed,alias]),before);
    console.log('MARROW_TABLE_HEADER_ALIAS_OK keyed=5 alias=3 source_immutable=true');
    '''
    subprocess.run(['node', '-e', script], input=json.dumps([keyed, alias]), text=True, check=True)


if __name__ == '__main__':
    main()
