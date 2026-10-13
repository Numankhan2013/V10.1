#!/usr/bin/env python3
"""Exercise actual table normalizer against both immutable source schemas."""
import json
import re
import subprocess
from pathlib import Path

from inventory_marrow_explanations import load_sharded
from app_page import app_source

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / 'app/src/main/assets/index.html'
MARKER = '  // NK_MARROW_STRUCTURED_TABLE_RENDERER_V1'


def main():
    page = app_source()
    assert page.count(MARKER) == 1, 'Marrow structured-table renderer missing'
    start = page.index(MARKER)
    helper = page[start:page.index('  const NK_MARROW_EXPLANATION_GOLD_V1=', start)]
    assert 'function nkRenderMarrowTableCompat(table)' in helper
    calls = re.findall(r"tables\.map\(\s*(nkRenderMarrowTable\w*)\s*\)\.join\(\s*''\s*\)", page)
    assert calls == ['nkRenderMarrowTableCompat'] * 2, calls
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
